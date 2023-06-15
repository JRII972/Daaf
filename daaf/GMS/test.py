import frappe

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
 
from datetime import datetime
from frappe.model.document import Document
from daaf.GMS.unDeuxTroisClick import Haverst as Haverst_123Click
from daaf.sisep.doctype.lieux_mercuriale.lieux_mercuriale import LieuxMercuriale
from daaf.sisep.doctype.releve_mercuriale.releve_mercuriale import ReleveMercuriale
Settings = frappe.get_doc('GMS Recolteur')


class ReleveMercuriale():

       
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
                
        pass
    
    def get_doc(self) -> ReleveMercuriale:
        child = frappe.new_doc("Releve Mercuriale")
        child.update({
            'produit': self.produit,
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
            'nutriscore': self.poids_de_référence,
            'image': self.poids_de_référence,
            'bio': self.poids_de_référence,
            'origine': self.poids_de_référence,
            'pass': self.poids_de_référence,
            'prevent_calculation': self.poids_de_référence,
            # 'parenttype': 'Prix et Marche',
            # 'parentfield': 'relevé',
        })
        
        return child

    def get_product_name(produit:str) -> Document: #Product from daaf module
        query = frappe.db.sql("""
        SELECT *, similarity/compare FROM
        (
            SELECT 
                name,
                SIMILARITY_STRING(%(produit)s, name) as similarity,
                COMPARE_STRING(%(produit)s, name) as compare,
                REPLACE(name, ' ', '|')
            FROM tabProduit
            WHERE %(produit)s REGEXP REPLACE(name, ' ', '|') 
        ) as q
        WHERE (similarity/compare) > %(similarity_limit)s
        ORDER BY compare, similarity DESC
        """, {
        'produit': produit,
        'similarity_limit' : Settings.limite_similarité_détection_nom_de_produit,
        
        } ,as_list=1)
        if len(query) == 0 : return Settings.aucun_produit_trouvé
        return query[0][0]

    @property
    def produit(self):
        return self._produit
    
    @produit.setter
    def produit(self, value:str):
        self._produit = ReleveMercuriale.get_product_name(value)
    
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
        self._lieu = frappe.get_doc('Lieux Mercuriale', value)  
        
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
        self._unité_de_vente = value #frappe.get_doc('Unite', value)  
        
    @property
    def unité_de_référence(self):
        return self._unité_de_référence
    
    @unité_de_référence.setter
    def unité_de_référence(self, value:str):
        self._unité_de_référence = value #frappe.get_doc('Unite', value)  

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
    def origine(self, value:bool):
        self._origine = value
    
class ReleveMercuriale123Click(ReleveMercuriale):
            
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
        self.commentaire = data['commentaire']
        self.prevent_check = True
        self.prevent_validation = False
        self.prevent_calculation = True
        self.nutriscore = data['nutriscore']
        self.image = data['image']
        self.bio = data['bio']
        self.origine = None
        
        super().__init__()
    
       
@frappe.whitelist()
def test():
    frappe.msgprint('Start')
    data = Haverst_123Click()
    frappe.msgprint('Havrest done')
    print('rrr')
    doc = frappe.new_doc('Prix et Marche')
    doc.date = datetime.today()
    doc.lieu = frappe.get_doc('Lieux Mercuriale', 'Dillon') 

    for row in data['data']:
        row = ReleveMercuriale123Click(row, datetime.today(), 'Dillon')
        doc.relevé.append(row.get_doc())
        
    doc.insert(
        ignore_permissions=True, # ignore write permissions during insert
        ignore_links=True, # ignore Link validation in the document
        ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
        ignore_mandatory=True # insert even if mandatory fields are not set
    )
    print(doc)
    return {'doc' : doc}