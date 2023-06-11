import frappe

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
 
from daaf.GMS.unDeuxTroisClick import Haverst as Haverst_123Click

@frappe.whitelist()
def test():
    return Haverst_123Click()