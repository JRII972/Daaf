# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import pandas as pd
import os 
from datetime import datetime
from daaf.GMS.releve_mercuriale import ReleveMercurialeLegacy
from frappe.utils import pretty_date  

logger = frappe.logger("sisep", allow_site=True, file_count=50)


@frappe.whitelist()
def checkRunningJob():
	jobQ = frappe.get_list('RQ Job', 
			filters={    
				'status': 'started',
				'job_name': 'Importation donne Mercuriale via CSV',
				},
	) + frappe.get_list('RQ Job', 
			filters={    
				'status': 'queued',
				'job_name': 'Importation donne Mercuriale via CSV',
				},
	) + frappe.get_list('RQ Job', 
			filters={    
				'status': 'deferred',
				'job_name': 'Importation donne Mercuriale via CSV',
				},
	)
 
	if len(jobQ) > 0 :
		try :
			sec = frappe.utils.format_duration((datetime.now(jobQ[0]['started_at'].tzinfo) - jobQ[0]['started_at']).total_seconds())
		except :
			sec = "Non lancé - patienter"
		frappe.throw("Une importation est déjà encours ! <hr> Lancer par : {} <br> Il y a {} <br> Actif depuis {}".format(
			jobQ[0]['owner'], 
			frappe.utils.pretty_date(jobQ[0]['creation'].strftime('%Y-%m-%d %H:%M:%S.%f')), 
			sec)
		)
  
	return True

class ImportationdonneeMercuriale(Document):
	def before_insert(self) :
		checkRunningJob()
	def on_submit(self):
		checkRunningJob()
		# Timeout 20 min
		frappe.enqueue(ImportData, job_name = 'Importation donne Mercuriale via CSV', enqueue_after_commit = True, timeout = 25000 ,docName=self.name, user = self.owner)


def ImportData(docName, user):
	Form = frappe.get_doc('Importation donnee Mercuriale', docName)
	Settings = frappe.get_doc('GMS Recolteur')
	try : 
		export = pd.read_csv(frappe.get_site_path() + Form.csv, sep=";", decimal=',', encoding='ISO-8859-1')
	except : 
		try : 
			export = pd.read_csv(frappe.get_site_path() + '/private' + Form.csv, sep=";", decimal=',', encoding='ISO-8859-1')
		except : 
			export = pd.read_csv(frappe.get_site_path() + '/public' + Form.csv, sep=";", decimal=',', encoding='ISO-8859-1')
	export = export[export['Superficie_plantée'].isnull()]
	export = export[export['Superficie_récoltée'].isnull()]
	export = export[export['mode de production'].isnull()]

	export = export[export['ID_LIEU'].notnull()]
	export = export[export['ID_LIEU'] != 1]

	export[['ID_LIEU', 'Réf Produit', 'Quantité', 'Prix unitaire']] = export[['ID_LIEU', 'Réf Produit', 'Quantité', 'Prix unitaire']].apply(pd.to_numeric)

	export = export[export['Réf Produit'] > 0]
	export = export[export['Quantité'] > 0]
	export = export[export['Prix unitaire'] > 0]

	export['date collecte'] = pd.to_datetime(export['date collecte'], format="%d/%m/%Y %H:%M:%S", errors = 'coerce')
	export = export[export['date collecte'] < datetime.now() ]
	export = export[export['date collecte'].notnull()]

	export = export[['ID_LIEU', 'date collecte', 'Réf Produit', 'Quantité', 'Prix unitaire']]

	produit = pd.read_csv(frappe.get_site_path() + Settings.legacy_produit , sep=';', encoding='ISO-8859-1' ) \
		.rename(columns={'nom': 'produit', 'code': 'Réf Produit'})[['produit', 'Réf Produit']]

	export = pd.merge(export, produit, on = "Réf Produit", how = "inner").sort_values(['ID_LIEU', 'date collecte'], ascending=[True, True])

	frappe.publish_progress(0, title='Importation CSV', description='Lecture du fichier CSV ...')

	data_size = len(export)
	releve = frappe.new_doc('Prix et Marche')
	i = 0
	for index, row in export.iterrows():
		_lieu = (Settings.fdf_import if row['ID_LIEU'] == 3 else Settings.dillon_import)
		if releve == None :
			releve = frappe.new_doc('Prix et Marche')
			releve.date = row['date collecte']
			releve.rayon = 'r'
			releve.lieu = _lieu
		print(f'{index} : {row["date collecte"]} {row["ID_LIEU"]} {row["produit"]}', end='\r')
		
		if (releve.lieu != _lieu) | (releve.date != row['date collecte']):
			if len(releve.relevé) > 0 :
				print('Save to DB {}'.format(releve.name) )
				releve.insert(
					ignore_permissions=True, # ignore write permissions during insert
					#ignore_links=True, # ignore Link validation in the document
					# ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
					ignore_mandatory=True # insert even if mandatory fields are not set
				)
				try:
					notification = frappe.new_doc("Notification Log")
					notification.for_user = user
					notification.set("type", "Alert")
					notification.document_type = 'Prix et Marche'
					notification.document_name = releve.name
					notification.subject = '<b>Importation : %(lieu)s</b> <br> Relevé d\'il ya %(date)s <br> %(produits)s produits importer ' % {
						'lieu' : releve.lieu ,
						'date' : pretty_date(releve.date),
						'produits' : len(releve.relevé),
						
					}
					notification.insert()
				except Exception:
					logger.error("Failed to send reminder", exc_info=1) 
				frappe.db.commit()
			
			releve = frappe.new_doc('Prix et Marche')
			releve.date = row['date collecte']
			# releve.rayon = 'r'
			releve.lieu = _lieu
			releve.importation = True
			child = ReleveMercurialeLegacy(row)
			releve.relevé.append(child.get_doc())

		child = ReleveMercurialeLegacy(row)
		releve.relevé.append(child.get_doc())
		i += 1
		frappe.publish_progress(i/data_size * 100, title='Importation CSV', description='Lecture du fichier CSV ...')