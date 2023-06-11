# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt


from frappe.model.document import Document

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from pypika.functions import Avg, Max, Min, Sum
from frappe.model.document import Document
from frappe.utils import getdate
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

class Lignecommentairemercuriale(Document):
	pass


@frappe.whitelist()
def MercurialeTbl(lieu, date = getdate()):
	if type(date) == str : date = datetime.strptime(date, f'%Y-%m-%d')
	Relevés = DocType("Releve Mercuriale") # you can also use frappe.qb.DocType to bypass an import
	Prix_et_marche = frappe.qb.DocType('Prix et Marche')

	count_all = Count('*').as_("count")
	prixAvg = Avg(Relevés.prix_vente)
	prixMax = Max(Relevés.prix_vente).as_('prixMax')
	prixMin = Min(Relevés.prix_vente).as_('prixMin')
	qtt = Sum(Relevés.poids_de_référence * Relevés.quantité_sur_l_étale).as_('qtt')

	LieuxMercuriale = frappe.db.sql("""
		WITH RECURSIVE LieuxMercurialeArbre AS (
			SELECT name,
				is_group,
				parent_lieux_mercuriale,
				0 AS generation_number
			FROM `tabLieux Mercuriale`
			WHERE name=%(lieu)s
		
		UNION ALL
		
			SELECT child.name,
				child.is_group,
				child.parent_lieux_mercuriale,
				generation_number+1 AS generation_number
			FROM `tabLieux Mercuriale` child
			JOIN LieuxMercurialeArbre g
			ON g.name = child.parent_lieux_mercuriale
		)

		SELECT name FROM LieuxMercurialeArbre
	""", values={'lieu' : lieu}, as_list=0)[0]

	actual = frappe.qb.from_(Relevés) \
			.inner_join(Prix_et_marche) \
			.on(Prix_et_marche.name == Relevés.parent)\
			.where(
				(Relevés.lieu.isin(LieuxMercuriale)) & (Prix_et_marche.Docstatus == 1) &
				(Relevés.date[date.replace(day=1):date + relativedelta(day=31)])
			) \
			.groupby(Relevés.produit) \
			.select(Relevés.produit, count_all, qtt, prixAvg.as_('prix'), prixMax, prixMin) \
			.having(
				count_all > 2
			)
   
	previous = frappe.qb.from_(Relevés) \
      		.inner_join(Prix_et_marche) \
       		.on(Prix_et_marche.name == Relevés.parent)\
			.where(
				(Relevés.lieu.isin(LieuxMercuriale)) & (Prix_et_marche.Docstatus == 1) &
				(Relevés.date[(date - timedelta(days=date.day)).replace(day=1) :(date - timedelta(days=date.day)) + relativedelta(day=31)])
			) \
			.groupby(Relevés.produit) \
			.having(
				count_all > 2
			).select(Relevés.produit,  prixAvg.as_('prixPre'))
   
	variation = ((actual.prix/previous.prixPre - 1 )*100).as_('variation')
 
	print(frappe.qb.from_(actual) \
     		.left_join(previous) \
       		.on(actual.produit == previous.produit)\
            .select(actual.produit, actual.count, actual.prix, actual.qtt, actual.prixMin, actual.prixMax, previous.prixPre, variation))
 
	return {
		'data' : (frappe.qb.from_(actual) \
     		.left_join(previous) \
       		.on(actual.produit == previous.produit)\
            .select(actual.produit, actual.count, actual.prix, actual.qtt, actual.prixMin, actual.prixMax, previous.prixPre, variation)).run()
	}