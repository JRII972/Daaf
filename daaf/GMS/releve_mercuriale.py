import frappe
from datetime import datetime
import pandas as pd
from daaf.sisep.doctype.lieux_mercuriale.lieux_mercuriale import LieuxMercuriale
from daaf.sisep.doctype.releve_mercuriale.releve_mercuriale import ReleveMercuriale
from daaf.GMS.scrapper import detectUnite

class ReleveMercurialeWrapper():
    _create_produit = False
       
    def __init__(self, **kwargs) -> None:
        if 'data' in kwargs : 
            if isinstance(kwargs['data'], dict) : 
                data = kwargs['data']
                self.produit = data['produit']
                self.date = data['date']
                self.lieu = data['lieu']
                self.prix_vente = data['prix_vente']
                self.prix_de_référence = data['prix_de_référence']
                self.poids_de_l_unité_de_vente = data['poids_de_l_unité_de_vente']
                self.poids_de_référence = data['poids_de_référence']
                self.quantité_sur_l_étale = data['quantité_sur_l_étale']
                self.unité_de_vente = data['unité_de_vente']
                self.unité_de_référence = data['unité_de_référence']
                self.commentaire = data['commentaire']
                self.prevent_check = data['prevent_check']
                self.prevent_validation = data['prevent_validation']
                self.prevent_calculation = data['prevent_calculation']
                self.nutriscore = data['nutriscore']
                self.image = data['image']
                self.bio = data['bio']
                self.origine = data['origine']
                self.lien_du_produit = data['lien_du_produit']
                
        pass
    
    def get_doc(self) -> ReleveMercuriale:
        child = frappe.new_doc("Releve Mercuriale")
        child.update({
            # 'produit': self.produit,
            'date': self.date,
            'lieu': self.lieu,
            'prix_vente': self.prix_vente,
            'prix_de_référence': self.prix_de_référence,
            'poids_de_l_unité_de_vente': self.poids_de_l_unité_de_vente,
            'poids_de_référence': self.poids_de_référence,
            'quantité_sur_l_étale': self.quantité_sur_l_étale,
            'unité_de_vente': self.unité_de_vente,
            'unité_de_référence': self.unité_de_référence,
            'commentaire': self.commentaire,
            'nutriscore': self.nutriscore,
            'image': self.image,
            'bio': self.bio,
            'origine': self.origine,
            'nom_affiché': self.nom_affiché,
            'prevent_calculation': self.prevent_calculation,
            'prevent_check': self.prevent_check,
            'prevent_validation': self.prevent_validation,
            'lien_du_produit': self.lien_du_produit,
            'parenttype': 'Prix et Marche',
            'parentfield': 'relevé',
        })
        child.produit = child.get_product_name(self._create_produit)
        return child

    @property
    def lien_du_produit(self):
        return self._lien_du_produit
    
    @lien_du_produit.setter
    def lien_du_produit(self, value:str):
        self._lien_du_produit = value
        
    @property
    def nom_affiché(self):
        return self._nom_affiché
    
    @nom_affiché.setter
    def nom_affiché(self, value:str):
        self._nom_affiché = value
        
    @property
    def produit(self):
        return self._produit
    
    @produit.setter
    def produit(self, value:str):
        self.nom_affiché = value
        self._produit = value
    
    @property
    def date(self):
        return self._date
    
    @date.setter
    def date(self, value:datetime):
        self._date = value  
    
    @property
    def lieu(self) -> LieuxMercuriale:
        return self._lieu
    
    @lieu.setter
    def lieu(self, value:str):
        self._lieu = frappe.get_doc('Lieux Mercuriale', value).get_title()  
        
    @property
    def prix_vente(self):
        return self._prix_vente
    
    @prix_vente.setter
    def prix_vente(self, value:float):
        self._prix_vente = value  
        
    @property
    def prix_de_référence(self):
        return self._prix_de_référence
    
    @prix_de_référence.setter
    def prix_de_référence(self, value:float):
        self._prix_de_référence = value  
        
    @property
    def poids_de_l_unité_de_vente(self):
        return self._poids_de_l_unité_de_vente
    
    @poids_de_l_unité_de_vente.setter
    def poids_de_l_unité_de_vente(self, value:float):
        self._poids_de_l_unité_de_vente = value  
        
    @property
    def poids_de_référence(self):
        return self._poids_de_référence
    
    @poids_de_référence.setter
    def poids_de_référence(self, value:float):
        self._poids_de_référence = value  
        
    @property
    def quantité_sur_l_étale(self):
        return self._quantité_sur_l_étale
    
    @quantité_sur_l_étale.setter
    def quantité_sur_l_étale(self, value:float):
        self._quantité_sur_l_étale = value  
        
    @property
    def unité_de_vente(self):
        return self._unité_de_vente
    
    @unité_de_vente.setter
    def unité_de_vente(self, value:str):
        if value == None : 
            self._unité_de_vente = None
            return None
        self._unité_de_vente = detectUnite(frappe.get_doc('Unite', value).get_title())  
        
    @property
    def unité_de_référence(self):
        return self._unité_de_référence
    
    @unité_de_référence.setter
    def unité_de_référence(self, value:str):
        self._unité_de_référence = detectUnite(frappe.get_doc('Unite', value).get_title())  

    @property
    def commentaire(self):
        return self._commentaire
    
    @commentaire.setter
    def commentaire(self, value:str):
        self._commentaire = value

    @property
    def prevent_validation(self):
        return self._prevent_validation
    
    @prevent_validation.setter
    def prevent_validation(self, value:bool):
        self._prevent_validation = value

    @property
    def prevent_check(self):
        return self._prevent_check
    
    @prevent_check.setter
    def prevent_check(self, value:bool):
        self._prevent_check = value
    
    @property
    def prevent_calculation(self):
        return self._prevent_calculation
    
    @prevent_calculation.setter
    def prevent_calculation(self, value:bool):
        self._prevent_calculation = value
    
    @property
    def nutriscore(self):
        return self._nutriscore
    
    @nutriscore.setter
    def nutriscore(self, value:bool):
        self._nutriscore = value
    
    @property
    def image(self):
        return self._image
    
    @image.setter
    def image(self, value:bool):
        self._image = value
    
    @property
    def bio(self):
        return self._bio
    
    @bio.setter
    def bio(self, value:bool):
        self._bio = value
    
    @property
    def origine(self):
        return self._origine
    
    @origine.setter
    def origine(self, value):
        if not value : value = None
        self._origine = value
    
    
class ReleveMercuriale123Click(ReleveMercurialeWrapper):
            
    def __init__(self, data:dict, date:datetime, lieu) -> None: #123_Click
        self.produit = data['produit']
        self.date = date
        self.lieu = lieu
        self.prix_vente = data['prix_vente']
        self.prix_de_référence = data['prixUnitaire']
        self.poids_de_l_unité_de_vente = data['poids_de_l_unité_de_vente']
        self.poids_de_référence = 1
        self.quantité_sur_l_étale = None
        self.unité_de_vente = None #data['unité_de_vente']
        self.unité_de_référence = data['unité_de_référence']
        self.commentaire = data['tag'] + '\n' + data['produit'] + '\n' + data['commentaire']
        self.prevent_check = True
        self.prevent_validation = False
        self.prevent_calculation = True
        self.nutriscore = data['nutriscore']
        self.image = data['image']
        self.bio = True if data['bio'] else False
        self.lien_du_produit = data['lien']
        self.origine = None
        
        super().__init__()
    
class ReleveMercurialeLegacy(ReleveMercurialeWrapper):
    def __init__(self, row:pd.core.series.Series, **kwargs) -> None:
        Settings = frappe.get_doc('GMS Recolteur')
        self._create_produit = True
        self.date = row['date collecte']
        self.lieu = Settings.fdf_import if row['ID_LIEU'] == 3 else Settings.dillon_import
        self.quantité_sur_l_étale = row['Quantité']
        self.prix_de_référence = row['Prix unitaire']
        self.unité_de_référence = Settings.legacy_unite
        self.nom_affiché = row['produit']
        
        self.raison_tendance = row['conjoncture-motif']
        self.tendance_constaté = row['conjoncture-tendance']
        
        self.prix_vente = row['Prix unitaire']
        self.poids_de_l_unité_de_vente = 1
        self.poids_de_référence = 1
        self.unité_de_vente = Settings.legacy_unite
        self.commentaire = None
        self.prevent_check = False
        self.prevent_validation = False
        self.prevent_calculation = True
        self.nutriscore = None
        self.image = None
        self.bio = False
        self.origine = 'Martinique'
        self.lien_du_produit = None
        super().__init__(**kwargs)
        
    def get_doc(self) -> ReleveMercuriale:
        child = frappe.new_doc("Releve Mercuriale")
        child.update({
            # 'produit': self.produit,
            'date': self.date,
            'lieu': self.lieu,
            'prix_vente': self.prix_vente,
            'prix_de_référence': self.prix_de_référence,
            'poids_de_l_unité_de_vente': self.poids_de_l_unité_de_vente,
            'poids_de_référence': self.poids_de_référence,
            'quantité_sur_l_étale': self.quantité_sur_l_étale,
            'unité_de_vente': self.unité_de_vente,
            'unité_de_référence': self.unité_de_référence,
            'commentaire': self.commentaire,
            'nutriscore': self.nutriscore,
            'image': self.image,
            'bio': self.bio,
            'origine': self.origine,
            'nom_affiché': self.nom_affiché,
            'prevent_calculation': self.prevent_calculation,
            'prevent_check': self.prevent_check,
            'prevent_validation': self.prevent_validation,
            'lien_du_produit': self.lien_du_produit,
            'tendance_constaté': self.tendance_constaté,
            'raison_tendance': self.raison_tendance,
            'parenttype': 'Prix et Marche',
            'parentfield': 'relevé',
        })
        child.produit = child.get_product_name(self._create_produit)
        return child