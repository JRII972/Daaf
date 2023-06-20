
import os
import zipfile
import frappe
from .settings import Settings

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
# Configuration de chrome Driver voir documentation
import frappe 
logger = frappe.logger("sisep", allow_site=True, file_count=50)
manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (Settings['PROXY_HOST'], Settings['PROXY_PORT'], Settings['PROXY_USER'], Settings['PROXY_PASS'])


def get_chromedriver(use_proxy=False, user_agent=None):
    use_proxy = False #TODO: remove 
    path = os.path.dirname(os.path.abspath(
        'C:/Users/jeremy.jovinac/Desktop/selenium/caper.ipynb'))
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Remote(
        command_executor='http://sisepserver:4444',
        options=chrome_options
    )
    return driver


def get_driver(use_proxy=False, user_agent=None):
    return get_chromedriver(use_proxy=False, user_agent=None)


def highlight(element, effect_time, color, border):
    import time
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent

    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                              element, s)
    original_style = element.get_attribute('style')
    apply_style("border: {0}px solid {1};".format(border, color))
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    time.sleep(effect_time)
    apply_style(original_style)

def detectUnite(name: str):
    try :
        Unités = frappe.get_all('Unite', 
        fields = ['name', 'tags', 'symbole'],
        limit_page_length = (
            frappe.qb.from_(DocType("Unite")) \
                .select( Count('*').as_("count"))
            ).run()[0][0]
        )

        for unite in Unités :
            if (name == unite['name']) | (name == unite['symbole']) : return unite['name']
            if unite['tags'] != None : 
                if name in unite['tags'].split(';') : return unite['name']
                print(unite['tags'].split(';') )
            
        try :
            if Settings.crée_unité_inexistence :
                _new_unite = frappe.new_doc('Unite', name)
                _new_unite.symbole = frappe.utils.get_abbr(name, max_len=3)  #TODO: Auto symbole
                _new_unite.coef = 1
                _new_unite.unitaire = 1
                _new_unite.insert(
                    ignore_permissions=True, # ignore write permissions during insert
                    )
                frappe.db.commit()
                return name
        except : 
            logger.error('Erreur lors de la création de l\'unite')
            
    except : 
        logger.error('Erreur lors de la création de l\'unite - lvl1')
        
    return Settings.unité_par_défaut