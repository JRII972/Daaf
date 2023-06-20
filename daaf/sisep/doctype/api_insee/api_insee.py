# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt

import pytz
import frappe
import datetime
from frappe.model.document import Document


class APIINSEE(Document):

	def get_expire_time(self):
		return datetime.datetime.strptime(self.expire_time, '%Y-%m-%d %H:%M:%S.%f') #'2023-06-27 14:15:20.814447'
    

	def set_expire_time(self, value:float):
		self.expire_time = pytz.UTC.localize(value)  
        
