# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from pypika.functions import Avg, StdDev
from frappe.model.document import Document
from frappe.utils import getdate


class PrixetMarche(Document):
	pass

@frappe.whitelist()
def PrixMarchePrixAvg(produit, date = getdate()):
	Releve = DocType("Releve Mercuriale") # you can also use frappe.qb.DocType to bypass an import

	count_all = Count('*').as_("count")
	prixAvg = Avg(Releve.prix_ref)
	prixStdDev = StdDev(Releve.prix_ref)

	result = (
		frappe.qb.from_(Releve) \
   			.where(Releve.produit == "Banane") \
          	.groupby(Releve.produit) \
           .select(Releve.produit, count_all, prixAvg, prixStdDev) 
			#.where(Web_Page_View.creation[some_date:some_later_date])
	).run()