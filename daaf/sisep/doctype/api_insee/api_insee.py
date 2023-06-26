# Copyright (c) 2023, SISEP - DAAF and contributors
# For license information, please see license.txt

import pytz
import frappe
import datetime
from frappe.model.document import Document
import requests
from requests.auth import HTTPBasicAuth

class APIINSEE(Document):

	def get_expire_time(self):
		return datetime.datetime.strptime(self.expire_time, '%Y-%m-%d %H:%M:%S.%f') #'2023-06-27 14:15:20.814447'
    

	def set_expire_time(self, value:float):
		self.expire_time = pytz.UTC.localize(value)  
        
	def getToken(self):
		API_SETTINGS = self
		headers = {
		'Authorization': 'Basic Base64(abc:cde)',
		'Content-Type': 'application/x-www-form-urlencoded',
		}

		payload='grant_type=client_credentials'
		r = requests.request("POST", API_SETTINGS.url, auth=HTTPBasicAuth(API_SETTINGS.insee_consumer_key , API_SETTINGS.insee_consumer_secret ), data=payload)
		print(r.json())
		API_SETTINGS.token = r.json()['access_token']
		timestamp = datetime.datetime.now() + datetime.timedelta(seconds= int(r.json()['expires_in']))
		API_SETTINGS.expire_time = pytz.UTC.localize(timestamp)
		API_SETTINGS.save()
  
		# Push to db
		frappe.db.commit()
		return self.token