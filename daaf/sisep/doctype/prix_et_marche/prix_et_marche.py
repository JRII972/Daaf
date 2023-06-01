# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from pypika.functions import Avg, StdDev
from frappe.model.document import Document
from frappe.utils import getdate
from datetime import datetime
from dateutil.relativedelta import relativedelta

class PrixetMarche(Document):
	pass

@frappe.whitelist()
def PrixMarchePrixAvg(produit, lieu, date = getdate()):
	if type(date) == str : date = datetime.strptime(date, '%Y-%m-%d')
	Releve = DocType("Releve Mercuriale") # you can also use frappe.qb.DocType to bypass an import
	Prix_et_marche = frappe.qb.DocType('Prix et Marche')
 
	count_all = Count('*').as_("count")
	prixAvg = Avg(Releve.prix_vente)
	prixStdDev = StdDev(Releve.prix_vente)

	result = (
		frappe.qb.from_(Releve) \
			.inner_join(Prix_et_marche) \
       		.on(Prix_et_marche.name == Releve.parent)\
   			.where(
				(Releve.lieu == lieu) & (Releve.produit == produit) & 
    			(Releve.date[date - relativedelta(months=+6):date]) &
				(Prix_et_marche.Docstatus == 1)
          	) \
          	.groupby(Releve.produit) \
           .select(Releve.produit, count_all, prixAvg, prixStdDev)
           .having( (count_all > 10) &  (prixStdDev > (3.5/count_all))) 
	).run()
 
	# print(frappe.qb.from_(Releve) \
	# 		.inner_join(Prix_et_marche) \
    #    		.on(Prix_et_marche.name == Releve.parent)\
   	# 		.where(
	# 			(Releve.produit == produit) & (Releve.date[date - relativedelta(months=+6):date]) &
	# 			(Prix_et_marche.Docstatus == 1)
    #       	) \
    #       	.groupby(Releve.produit) \
    #        .select(Releve.produit, count_all, prixAvg, prixStdDev) )
	# print(result)
 
	if len(result) == 0 : 
		return {
			'Error': True
		}
  
	else : return {
		'produit': produit,
		'avg' : result[0][2],
		'StdDev' : result[0][3]
	}