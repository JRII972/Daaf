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

def get_product_name(produit) -> Document: #Product from daaf module
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
    'produit': produit,
    'similarity_limit' : Settings.limite_similarité_détection_nom_de_produit,
    'regexmin' : Settings.limite_sous_séquence,
    'likemin' : Settings.limite_sous_séquence_multiple,
    
    } ,as_list=1)
    print(query)
    if len(query) == 0 : return Settings.aucun_produit_trouvé
    return query[0][0]

def clear_sessions(session_id=None):
    import requests, json
    """
    Here we query and delete orphan sessions
    docs: https://www.selenium.dev/documentation/grid/advanced_features/endpoints/
    :return: None
    """
    url = "http://127.0.0.1:4444"
    if not session_id:
        # delete all sessions
        r = requests.get("{}/status".format(url))
        data = json.loads(r.text)
        for node in data['value']['nodes']:
            for slot in node['slots']:
                if slot['session']:
                    id = slot['session']['sessionId']
                    r = requests.delete("{}/session/{}".format(url, id))
    else:
        # delete session from params
        r = requests.delete("{}/session/{}".format(url, session_id))
        
