# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
from frappe.model.naming import make_autoname
import time, requests

class Etablissements(Document):
	def autoname(self):
		# if self.name : return
		if (self.denomination_unite_legale) : self.name = self.denomination_unite_legale
		elif (self.denomination_usuelle_1_unite_legale) : self.name = self.denomination_usuelle_1_unite_legale
		elif (self.caractere_employeur_unite_legale == 'N') : 
			if (self.prenom_usuel_unite_legale) : self.name = self.prenom_usuel_unite_legale 
			if (self.nom_unite_legale) : self.name = self.name + ' '  + self.nom_unite_legale 
			if (self.denomination_usuelle_1_unite_legale) : self.name = self.name + ' ' + self.denomination_usuelle_1_unite_legale
			elif (self.libelle_commune_etablissement) : self.name = self.name + ' ' +self.libelle_commune_etablissement
		elif self.denomination_usuelle_1_unite_legale :
			self.name = self.denomination_usuelle_1_unite_legale
			
		if frappe.db.exists(self.doctype, self.name):
			if (self.libelle_commune_etablissement) : self.name = self.name + ' ' +self.libelle_commune_etablissement
			if frappe.db.exists(self.doctype, self.name):
				if (self.libelle_voie_etablissement) : self.name = self.name + ' ' +self.libelle_voie_etablissement
				if frappe.db.exists(self.doctype, self.name):
					self.name = self.name + ' ' + make_autoname(
						".#"
					)

	@classmethod
	def update_from_insee(cls):
		frappe.enqueue(cls._upate_from_insee, queue='long', timeout=cls.get_perf_update_from_insee(), is_async=True, job_name='Update db from INSEE API')
  
	@classmethod
	def _upate_from_insee(cls):
		API_SETTINGS = frappe.get_doc('API INSEE')
		curseur = '*'
		headers = {
			'Accept': 'application/json',
			'Authorization': 'Bearer {}'.format(API_SETTINGS.getToken()),
		}
		start_time = time.time()
		i = 0
		while True :
			response = requests.get(f'https://api.insee.fr/entreprises/sirene/V3/siret?q=codePostalEtablissement%3A972*&curseur={curseur}', headers=headers)
			print(f"--- {response.json()['header']['message']} {curseur} / {response.json()['header']['nombre']*i} - {time.time() - start_time} seconds ---", end='\r')
			i+=1
			if response.json()['header']['statut'] == 200 :
				if (curseur != response.json()['header']['curseurSuivant']):
					curseur = response.json()['header']['curseurSuivant']
				else : break
				
			for ets in response.json()['etablissements'] :
				Etablissements.load_insee(ets)
				
			frappe.db.commit()
			
  
	@classmethod
	def get_perf_update_from_insee(cls):
		API_SETTINGS = frappe.get_doc('API INSEE')
		curseur = '*'
		headers = {
			'Accept': 'application/json',
			'Authorization': 'Bearer {}'.format(API_SETTINGS.getToken()),
		}
  
		# Check perf
		start_time = time.time()
		response = requests.get(f'https://api.insee.fr/entreprises/sirene/V3/siret?q=codePostalEtablissement%3A972*&curseur={curseur}', headers=headers)
		_time_request = time.time() - start_time
		start_time = time.time()
		insee_data = response.json()['etablissements'][0]
		Etablissements.load_insee(insee_data)

		frappe.db.commit()
		_time_db = (time.time() - start_time) #* response.json()['header']['total']
		print(f"--- {_time_request} + {_time_db} seconds ---")
		_time_db *= response.json()['header']['total']
		_time_request *= response.json()['header']['total'] / response.json()['header']['nombre']
		print(f"--- {_time_request + _time_db} seconds total ---")
  
		return (_time_request + _time_db)*1.25 # Margin of 25%

	def load_insee(insee_data:dict):
		query = frappe.get_list('Etablissements', filters = {
			'siret' : insee_data['siret']
		})
		if (len(query) > 0) : Ets = frappe.get_doc('Etablissements', query[0]['name']).update_from_insee_data(insee_data).save(ignore_permissions=True)
		else : Ets = frappe.new_doc('Etablissements').update_from_insee_data(insee_data).insert(ignore_permissions=True)
		return Ets

	def load_PAC_exploitant(pac_data):
		query = frappe.get_list('Etablissements', filters = {
			'pacage' : pac_data['Pacage']
		}, order_by='modified desc') +  ( frappe.get_list('Etablissements', filters = {
			'siret' : pac_data['Siret']
		}, order_by='modified desc') if pac_data['Siret'] else [] )
		if (len(query) > 0) : Ets = frappe.get_doc('Etablissements', query[0]['name']).update_from_insee_data(pac_data).save(ignore_permissions=True)
		else : Ets = frappe.new_doc('Etablissements').update_from_insee_data(pac_data).insert(ignore_permissions=True)
		return Ets

	def update_from_pac(self, pac_data):
		self.pacage = pac_data['Pacage']
		self.etat_pacage = pac_data['Etat']
		self.date_début_validité_sigc = datetime.datetime.strptime(pac_data['Date début validité SIGC'], '%d/%m/%Y') if pac_data['Date début validité SIGC'] else None
		self.date_fin_validité_sigc = datetime.datetime.strptime(pac_data['Date fin validité SIGC'], '%d/%m/%Y')  if pac_data['Date fin validité SIGC'] else None
		self.date_clôture = datetime.datetime.strptime(pac_data['Date clôture'], '%d/%m/%Y')  if pac_data['Date clôture'] else None
		self.motif_clôture = pac_data['Motif clôture']
		self.date_installation = datetime.datetime.strptime(pac_data['Date installation'], '%d/%m/%Y') if pac_data['Date installation'] else None
		self.adresse_pac = ''
		if pac_data['Adresse siège 1'] : self.adresse_pac += pac_data['Adresse siège 1'] + '\n'
		if pac_data['Adresse siège 2'] : self.adresse_pac += pac_data['Adresse siège 2'] + '\n'
		if pac_data['Adresse siège 3'] : self.adresse_pac += pac_data['Adresse siège 3'] + '\n'
		if pac_data['Adresse siège 4'] : self.adresse_pac += pac_data['Adresse siège 4'] + '\n'
		if pac_data['Adresse siège 5'] : self.adresse_pac += pac_data['Adresse siège 5'] 
		self.téléphone_adresse_postale = pac_data['Téléphone adresse postale']
		self.téléphone_adresse_siège = pac_data['Téléphone adresse siège']
		self.forme_juridique_pac = pac_data['Forme juridique']
		self.portable_1 = pac_data['Portable 1'] if len(str(pac_data['Portable 1'])) >= 10 else None
		self.portable_2 = pac_data['Portable 2'] if len(str(pac_data['Portable 2'])) >= 10 else None
  
		# Generale Update
		self.siren = pac_data['Siret']
		self.denomination_unite_legale = pac_data['Nom - Raison sociale']
		self.sexe_unite_legale = 'M' if pac_data['Civilité'] == 'Monsieur' else ( 'F' if pac_data['Civilité'] == 'Madame' else '')
		self.nom_unite_legale = pac_data['Nom - Raison sociale'] if pac_data['Civilité'] else ''
		self.prenom_1_unite_legale = pac_data['Prénoms']
  
		return self


	def update_from_insee_data(self, insee_data):
		
		self.siren = insee_data['siren']
		self.siret = insee_data['siret']
		self.nic = insee_data['nic']
		
		self.date_creation_etablissement = insee_data['dateCreationEtablissement']
		self.tranche_effectifs_etablissement = insee_data['trancheEffectifsEtablissement']
		self.annee_effectifs_etablissement = (datetime.datetime(insee_data['anneeEffectifsEtablissement'], 12, 31) if type == int else datetime.datetime(int(insee_data['anneeEffectifsEtablissement']), 12, 31) ) if insee_data['anneeEffectifsEtablissement'] else insee_data['anneeEffectifsEtablissement']
		self.activite_principale_registre_metiers_etablissement = insee_data['activitePrincipaleRegistreMetiersEtablissement']
		self.etablissement_siege = insee_data['etablissementSiege']

		#Unite legal
		uniteLegal = insee_data['uniteLegale']
		self.date_creation_unite_legale = uniteLegal['dateCreationUniteLegale']
		self.sigle_unite_legale = uniteLegal['sigleUniteLegale']
		self.sexe_unite_legale = uniteLegal['sexeUniteLegale']
		self.prenom_1_unite_legale = uniteLegal['prenom1UniteLegale']
		self.prenom_2_unite_legale = uniteLegal['prenom1UniteLegale']
		self.prenom_3_unite_legale = uniteLegal['prenom3UniteLegale']
		self.prenom_4_unite_legale = uniteLegal['prenom4UniteLegale']
		self.prenom_usuel_unite_legale = uniteLegal['prenomUsuelUniteLegale']
		self.pseudonyme_unite_legale = uniteLegal['pseudonymeUniteLegale']
		self.identifiant_association_unite_legale = uniteLegal['identifiantAssociationUniteLegale']
		self.tranche_effectifs_unite_legale = uniteLegal['trancheEffectifsUniteLegale']
		self.annee_effectifs_unite_legale = (datetime.datetime(uniteLegal['anneeEffectifsUniteLegale'], 12, 31) if type == int else datetime.datetime(int(uniteLegal['anneeEffectifsUniteLegale']), 12, 31) ) if uniteLegal['anneeEffectifsUniteLegale'] else uniteLegal['anneeEffectifsUniteLegale']
		self.categorie_entreprise = uniteLegal['categorieEntreprise']
		self.annee_categorie_entreprise = (datetime.datetime(uniteLegal['anneeCategorieEntreprise'], 12, 31) if type == int else datetime.datetime(int(uniteLegal['anneeCategorieEntreprise']), 12, 31) ) if uniteLegal['anneeCategorieEntreprise'] else uniteLegal['anneeCategorieEntreprise']
		self.etat_administratif_unite_legale = uniteLegal['etatAdministratifUniteLegale']
		self.nom_unite_legale = uniteLegal['nomUniteLegale']
		self.denomination_unite_legale = uniteLegal['denominationUniteLegale']
		self.denomination_usuelle_1_unite_legale = uniteLegal['denominationUsuelle1UniteLegale']
		self.denomination_usuelle_2_unite_legale = uniteLegal['denominationUsuelle2UniteLegale']
		self.denomination_usuelle_3_unite_legale = uniteLegal['denominationUsuelle3UniteLegale']
		self.activite_principale_unite_legale = uniteLegal['activitePrincipaleUniteLegale']
		self.categorie_juridique_unite_legale = uniteLegal['categorieJuridiqueUniteLegale']
		self.nic_siege_unite_legale = uniteLegal['nicSiegeUniteLegale']
		self.nomenclature_activite_principale_unite_legale = uniteLegal['nomenclatureActivitePrincipaleUniteLegale']
		self.nom_usage_unite_legale = uniteLegal['nomUsageUniteLegale']
		self.economie_sociale_solidaire_unite_legale = uniteLegal['economieSocialeSolidaireUniteLegale']
		self.societe_mission_unite_legale = uniteLegal['societeMissionUniteLegale']
		self.caractere_employeur_unite_legale = uniteLegal['caractereEmployeurUniteLegale']

		# Adresse
		adresse = insee_data['adresseEtablissement']
		self.complement_adresse_etablissement = adresse['complementAdresseEtablissement']
		self.numero_voie_etablissement = adresse['numeroVoieEtablissement']
		self.type_voie_etablissement = adresse['typeVoieEtablissement']
		self.libelle_voie_etablissement = adresse['libelleVoieEtablissement']
		self.code_postal_etablissement = adresse['codePostalEtablissement']
		self.libelle_commune_etablissement = adresse['libelleCommuneEtablissement']

		# periodesEtablissement
		periode = insee_data['periodesEtablissement'][0]
		self.date_fin = periode['dateFin']
		self.date_debut = periode['dateDebut']
		self.etat_administratif_etablissement = periode['etatAdministratifEtablissement']
		self.enseigne_1_etablissement = periode['enseigne1Etablissement']
		self.enseigne_2_etablissement = periode['enseigne2Etablissement']
		self.enseigne_3_etablissement = periode['enseigne3Etablissement']
		self.denomination_usuelle_etablissement = periode['changementEnseigneEtablissement']
		self.activite_principale_etablissement = periode['activitePrincipaleEtablissement']
		self.nomenclature_activite_principale_etablissement = periode['nomenclatureActivitePrincipaleEtablissement']
		self.caractere_employeur_etablissement = periode['caractereEmployeurEtablissement']

		return self
