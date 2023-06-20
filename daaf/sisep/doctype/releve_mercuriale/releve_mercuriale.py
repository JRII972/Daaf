# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ReleveMercuriale(Document):
	def get_product_name(self, _new = False) -> Document: #Product from daaf module
		Settings = frappe.get_doc('GMS Recolteur')
		query = frappe.db.sql(query="""
		SELECT produit, ((LIKENAME + SUM(LIKETAG))/MAX(compare)), LIKENAME + SUM(LIKETAG) as LIKEFILTER, REX + SUM(REXTAG) as REXGEX, MAX(similarity)
		FROM (  
			SELECT 
				tabProduit.name as produit, 
				`tabVariation produit`.name as tags, 
				%(produit)s LIKE CONCAT('%%', tabProduit.name, '%%') as LIKENAME,
				if(
					%(produit)s LIKE CONCAT('%%', `tabVariation produit`.name, '%%') IS NULL,
					0,
					%(produit)s LIKE CONCAT('%%', `tabVariation produit`.name, '%%')
				) as LIKETAG,
				%(produit)s REGEXP REPLACE(tabProduit.name, ' ', '|') as REX,
				if(
					%(produit)s REGEXP REPLACE(`tabVariation produit`.name, ' ', '|') IS NULL,
					0,
					%(produit)s REGEXP REPLACE(`tabVariation produit`.name, ' ', '|')
				) as REXTAG,
				if(
					SIMILARITY_STRING(%(produit)s, tabProduit.name) is NULL, 
					if(SIMILARITY_STRING(%(produit)s, `tabVariation produit`.name) is NULL, NULL, SIMILARITY_STRING(%(produit)s, `tabVariation produit`.name)), /* second NULL is default value */
					if(SIMILARITY_STRING(%(produit)s, `tabVariation produit`.name) is NULL, SIMILARITY_STRING(%(produit)s, tabProduit.name), GREATEST(SIMILARITY_STRING(%(produit)s, tabProduit.name), SIMILARITY_STRING(%(produit)s, `tabVariation produit`.name)))
				) as similarity,
				GREATEST(COMPARE_STRING(%(produit)s, tabProduit.name), COMPARE_STRING(%(produit)s, `tabVariation produit`.name)) as compare
			FROM tabProduit
			LEFT JOIN `tabVariation produit link` ON `tabVariation produit link`.parent = tabProduit.name
			LEFT JOIN `tabVariation produit` ON `tabVariation produit link`.variation = `tabVariation produit`.name
		) as q
		GROUP BY produit
		HAVING LIKEFILTER > %(likemin)s OR REXGEX > %(regexmin)s OR MAX(similarity) > %(similarity_limit)s 
		ORDER BY ((LIKENAME + SUM(LIKETAG))/MAX(compare)) DESC, LIKEFILTER DESC, MAX(similarity) DESC, REXGEX DESC
		""", values={
		'produit': self.nom_affiché,
		'similarity_limit' : Settings.limite_similarité_détection_nom_de_produit,
		'regexmin' : Settings.limite_sous_séquence,
		'likemin' : Settings.limite_sous_séquence_multiple,
		
		} ,as_list=1)
		print(query)
		if len(query) == 0 : 
			if _new :
				try :
					_new_produit = frappe.new_doc('Produit')
					_new_produit.nom = self.nom_affiché
					_new_produit.insert(
						ignore_permissions=True, # ignore write permissions during insert
						# ignore_links=True, # ignore Link validation in the document
						# ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
						ignore_mandatory=True # insert even if mandatory fields are not set
					)
					return _new_produit.name
				except Exception as e:
					print(e)
					self.log_error(message=f'Error while creating new produit {self.nom_affiché}')
			return Settings.aucun_produit_trouvé
		return query[0][0]
