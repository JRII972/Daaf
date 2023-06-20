# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate 

class ObservationmeteorologiquehistoriquesFranceSYNOP(Document):
	def autoname(self):
		# if self.name : return
		if not self.date :
			frappe.throw("La date est obligatoir")
		if not self.communes_name : 
			frappe.throw("La commune est obligatoir")
   
		self.name = f'SYNOP_{self.date}_{self.communes_name}'
