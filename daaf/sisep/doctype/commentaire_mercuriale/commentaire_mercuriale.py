# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
from frappe.utils import getdate

@frappe.whitelist()
def GenerateCommentaire(lieu:str, date):
    import locale
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    
    date = getdate(date)
    modèle = frappe.get_list('Modele Commentaire', 
                        filters={
						'lieu': lieu
					}
					) + frappe.get_list('Modele Commentaire', 
                        filters={
						'defaut': True
					}
					)
    if len(modèle) == 0 : 
        return f'Aucun modèle trouver. Renseigner un par default ou taper votre texte {type(date)}'
		

    return frappe.get_doc('Modele Commentaire', modèle[0]['name']).modèle % {
		'date' : date.strftime('%a %d/%m%y').title()
	}

class CommentaireMercuriale(Document):
	def before_save(self):
		if (not self.commentaire) | (self.commentaire == '') :
			self.commentaire = GenerateCommentaire(self.lieu, self.date)