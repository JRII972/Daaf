from pypika import CustomFunction
import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from pypika.functions import Avg, StdDev
from frappe.model.document import Document
from frappe.utils import getdate
from datetime import datetime
from dateutil.relativedelta import relativedelta

Settings = frappe.get_doc('GMS Recolteur')

def get_product_name(produit:str):
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