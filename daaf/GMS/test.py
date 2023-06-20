import frappe

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from babel.dates import format_datetime
from frappe.utils import pretty_date
from datetime import datetime
from frappe.model.document import Document
from daaf.GMS.unDeuxTroisClick import Haverst as Haverst_123Click
from daaf.sisep.doctype.lieux_mercuriale.lieux_mercuriale import LieuxMercuriale
from daaf.sisep.doctype.releve_mercuriale.releve_mercuriale import ReleveMercuriale
# Settings = frappe.get_doc('GMS Recolteur')

def long_running_job(param1, param2):
    # expensive tasks
    pass

@frappe.whitelist()
def test():
    _users = frappe.db.get_list('User', filters=[
        ['role','in', ['Mercuriale']]
    ])

    users = []
    for user in _users :
        users.append(user['name'])
        
    jobQ = frappe.get_list('RQ Job', 
			filters={    
				'status': 'queued',
				'job_name': 'Importation donne Mercuriale via CSV',
				},
	) + frappe.get_list('RQ Job', 
			filters={    
				'status': 'started',
				'job_name': 'Importation donne Mercuriale via CSV',
				},
	) + frappe.get_list('RQ Job', 
			filters={    
				'status': 'deferred',
				'job_name': 'Importation donne Mercuriale via CSV',
				},
	) #TODO add scheduled and so on

    if len(jobQ) > 0 :
        try :
            sec = frappe.utils.format_duration((datetime.now(jobQ[0]['started_at'].tzinfo) - jobQ[0]['started_at']).total_seconds())
        except :
            sec = "Non lancé - patienter"
                         
        frappe.msgprint("Une collect est déjà encours ! <hr> Lancer par : {} <br> A la date de {} <br> Actif depuis {}".format(
            jobQ[0]['owner'], 
            frappe.utils.pretty_date(jobQ[0]['creation'].strftime('%Y-%m-%d %H:%M:%S.%f')), 
            sec)
        )
        return 

    frappe.enqueue(Haverst_123Click, 
                    queue='long', 
                    job_name = "GMS - Collect Start - 123 Click",
                    lieu=frappe.get_doc('Lieux Mercuriale', '123 Click'), 
                    users=users)
    # data, docs = Haverst_123Click(
    #     frappe.get_doc('Lieux Mercuriale', '123 Click'),
    #         users
    #             ) 
    frappe.msgprint('Collect lancer')

    return {}