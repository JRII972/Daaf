import os
import io
import re
import requests
import pytesseract
from daaf.sisep.doctype.lieux_mercuriale.lieux_mercuriale import LieuxMercuriale
from IPython.display import Image
from json import loads, dumps
from rich.progress import Progress
import urllib.request
from PIL import Image
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
import datetime
import time
import random
from platformdirs import user_cache_dir
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import zipfile
import re
from selenium import webdriver
from daaf.GMS.scrapper import get_driver, detectUnite #, highlight
from daaf.GMS.settings import Settings
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

import frappe 
logger = frappe.logger("sisep", allow_site=True, file_count=50)

def startEngine(driver:webdriver = None):
    if driver == None : driver = get_driver()
    logger.info("Starg selenium web driver")
    try : 
        driver.get('https://martinique.123-click.com/')
    except : 
        frappe.log_error(frappe.get_traceback(), 'Echec collect, impossible ouvrir line 123 Click')

    # cookies / onetrust
    try : 
        # driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        WebDriverWait( driver, 30, ignored_exceptions=ignored_exceptions) \
                .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'a[class="cookie_btn_main accept"]'))).click()
    except : 
        logger.debug("trust already accept")
        
    return driver

# Detect si le produit récolter est viable
# TODO : Non implémenter : Ajouter les conditions de validation
# Lever un erreur dans le cas ou le produit n'est pas bon
# Cela bloquera l'enregistrement du produit, affichera une information pour le degugage, et passera au suivant


def dateEnhance(ProduitName:str ,prixVente: float, prixUnitaire: float, unitePrixUnitaire: str, Poids: float, uniteVente: str) -> tuple:
    try : 
        
        if (prixVente == None) & (prixUnitaire != None) & (unitePrixUnitaire != None) & (Poids != None) & (uniteVente != None):
            logger.debug("Not Implemented")


        if ('Œuf'.lower() in ProduitName.lower()) | ('oeufs' in ProduitName.lower()) & (uniteVente == 'unitaire'):
            if (prixVente == None) & (prixUnitaire != None) : 
                prixVente = prixUnitaire
            logger.debug(prixVente, Poids )
            prixUnitaire = prixVente / Poids
            unitePrixUnitaire = 'unitaire'
            
    except Exception as e :
        logger.debug(e)
    
    return prixVente, prixUnitaire, Poids, unitePrixUnitaire




def getProduit(driver:webdriver, produit: WebElement) -> tuple[str, int, int, str, float, str, str, str, str, str, str]:
    """Analyse et extraction des information du produit

    Analyse de l'HTLM du produit à récolter
    Dans le cas ou le format d'affichage du produit change
    C'est ici qu'il faut modifier la detection
    Pour la détection 

    Parameters:
    produit (WebElement): Le produit à analyse, doit se limite au plus que possible au bloque contenant un produit avec le moins de parasite de possible

    Returns:
    int:ProduitName
    int:prixVente
    int:Poids
    int:uniteVente
    int:prixUnitaire
    int:unitePrixUnitaire
    int:Origine
    int:information
    int:image
    int:Qualite
    int:Nutriscore
    str:Lien URL

    """


    # Prix de vente
    try:
        prixVente = float(produit.find_element(By.CSS_SELECTOR, '[class*="price-full"]').get_attribute("innerHTML").rstrip().removesuffix('€').replace(',', '.').rstrip().lstrip())
    except:
        prixVente = None

    # Produit
    try:
        Desc = produit.find_element(By.CSS_SELECTOR, '[class*="desc"]')
        ProduitName = Desc.find_element(
            By.CSS_SELECTOR, 'a').get_attribute("innerHTML").rstrip().lstrip()
    except Exception as e:
        ProduitName = None
        
    # Prix unitaire
    try:
        prixUnitaire = None
        unitePrixUnitaire = None
        
        match = re.search(r'\d+,\d+', produit.find_element(By.CSS_SELECTOR, '[class*="unity-price"]').get_attribute("innerHTML"))
        if match != None :
            prixUnitaire = float( match.group().replace(',', '.'))
    
        unitePrixUnitaire = produit.find_element(By.CSS_SELECTOR, '[class*="unity-price"] > em').get_attribute("innerHTML")
        unitePrixUnitaire = detectUnite(unitePrixUnitaire)
    except:
        prixUnitaire = None
        unitePrixUnitaire = None

    
        
    # Poids
    try:
        Poids = float(re.search(r'\d+', produit.find_element(By.CSS_SELECTOR, 'div[class*="poids-suffixe-holder"]').get_attribute("innerHTML")).group())
    except Exception as e:
        # logger.debug(e)
        Poids = None
        
    # uniteVente
    try:
        uniteVente = re.search(r'[a-zA-Z]+', produit.find_element(By.CSS_SELECTOR, 'div[class*="poids-suffixe-holder"]').get_attribute("innerHTML")).group()
        uniteVente = 'unitaire' if uniteVente.lower() == 'x' else uniteVente
        uniteVente = detectUnite(uniteVente)
    except Exception as e:
        # logger.debug(e)
        uniteVente = None

    # Origine
    try:
        Origine = None # Check in Product name
    except:
        Origine = None

    # Image
    try:
        image = produit.find_element(
            By.CSS_SELECTOR, '[class*="product-left"]').find_element(By.TAG_NAME, "img").get_attribute('src')
        
        if image == 'https://martinique.123-click.com/pub/design/Easy-Loader.gif' : 
            import time
            logger.info("Wait for image")
            for i in range(30):
                image = produit.find_element(
                    By.CSS_SELECTOR, '[class*="product-left"]').find_element(By.TAG_NAME, "img").get_attribute('src')
                if image != 'https://martinique.123-click.com/pub/design/Easy-Loader.gif' : break
                driver.execute_script(f"window.scrollTo(0, 0.{i});")
                time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.1);")
            
            
    except:
        image = None
        
    try:
        lien = produit.find_element(
            By.CSS_SELECTOR, '[class*="product-left"]').find_element(By.TAG_NAME, "a").get_attribute('href')
        
    except:
        lien = None

    # QUALITE
    try:
        bio = len(produit.find_elements(By.CSS_SELECTOR, '[class*="picto-vignette-item"][data-picto="bio"]')) > 0
        
        if (not bio) :
            bio = 'bio' in ProduitName.lower()

    except:
        bio = None

    # Nutriscore
    try:
        Nutriscore = produit.find_element(
            By.CSS_SELECTOR, '[class="picto-item nutri-score-item"] > img').get_attribute('src')

        if (Nutriscore == (Settings['123Click']['BaseURL'] + "pub/design/Picto/Nutriscore/Nutri-score-E.svg")):
            Nutriscore = 'E'
        elif (Nutriscore == (Settings['123Click']['BaseURL'] + "pub/design/Picto/Nutriscore/Nutri-score-D.svg")):
            Nutriscore = 'D'
        elif (Nutriscore == (Settings['123Click']['BaseURL'] + "pub/design/Picto/Nutriscore/Nutri-score-C.svg")):
            Nutriscore = 'C'
        elif (Nutriscore == (Settings['123Click']['BaseURL'] + "pub/design/Picto/Nutriscore/Nutri-score-B.svg")):
            Nutriscore = 'B'
        elif (Nutriscore == (Settings['123Click']['BaseURL'] + "pub/design/Picto/Nutriscore/Nutri-score-A.svg")):
            Nutriscore = 'A'
        else :
            Nutriscore = None
    except:
        Nutriscore = None

    prixVente, prixUnitaire, Poids, unitePrixUnitaire = dateEnhance(
        ProduitName, prixVente, prixUnitaire, unitePrixUnitaire, Poids, uniteVente)

    return ProduitName, prixVente, Poids, uniteVente, prixUnitaire, unitePrixUnitaire, Origine, image, bio, Nutriscore, lien




def GetRangeeProduit(driver:webdriver, rayon, tag):
    driver.get(rayon)

    # rayons = driver.find_element(By.CSS_SELECTOR, '[class*="FiltresNavigation"]')
    # list_rayons = {}

    # for i in rayons.find_elements(By.TAG_NAME, "A") :
    #     if i.get_attribute('innerHTML').strip().upper() != "TOUS" :
    #         list_rayons[i.get_attribute('innerHTML').strip()] = i.get_attribute('href')

    product_List = pd.DataFrame({
        'produit': [],
        'prix_vente': [],
        'poids_de_l_unité_de_vente': [],
        'unite': [],
        'prixUnitaire': [],
        'unité_de_référence': [],
        'origine': [],
        'image': [],
        'bio': [],
        'nutriscore': [],
        'lien' : [],
        'tag': [],
    })
    
    product_List["bio"]=product_List["bio"].astype(bool)

    # Wait for list produits present 
    listProduits = WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
        .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="product_list"]')))
    logger.info('Havresting : {tag}...')
    
    # Load the all page
    from time import sleep
    _old_url = ''
    while (driver.current_url != _old_url):
        _old_url = driver.current_url
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        
    # Wait xhr payload
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.9);")
    sleep(15)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.1);")
    
    while True:
        try :
            produit = WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
        .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="product-list-affichage-desktop"]')))
            
            if Settings['DEBUG'] : driver.execute_script("window.scrollTo(0, 0);")
            
            product_List.loc[len(product_List)] = np.append(np.asarray(getProduit(driver, produit)), tag)
            
            
            driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, produit)
        except Exception as e : 
            logger.debug(e)
            frappe.log_error(frappe.get_traceback(), '123 Click : Echec de la lecture d\'un produit')
            break    

    logger.debug(f'{len(product_List)} produits lu - {tag}')

    return product_List



def GetRayonLink(driver:webdriver) -> pd.DataFrame:
    driver.get(Settings['123Click']['BaseURL'])
    logger.info('Recherche des rayons...')
    
    WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
                .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="menu-item-holder rayons-holder"]'))).click()
    listRayons = WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
        .until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="category-list-holder category-list-small"] > a[class*="category-item"]')))
        
    rayon_lvl_1 = []

    RayonsList = pd.DataFrame({
                'cat': [],
                'produit': [],
                'lien': [],
            })

    for i in listRayons:
        rayon_lvl_1.append((i.find_element(By.CSS_SELECTOR, 'p[class="subtitle-item"]').get_attribute("innerText"), #Name
        i.get_attribute("href"))) #Lin
        
    rayon_lvl_1.pop(0)
    logger.debug('{} rayons trouver, recherche des sous rayons'.format(len(rayon_lvl_1)))
    for i in rayon_lvl_1 : 
        rayon_lvl_2 = []
        tag = i[0]
        driver.get(i[1])
        listRayons = WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
            .until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class*="categ-lvl-2"] > a[class*="category-item-small"]')))
        
        for i in listRayons:
            rayon_lvl_2.append((i.get_attribute("innerText"), #Name
            i.get_attribute("href"))) #Lin
            
        if len(rayon_lvl_2) > 1 : rayon_lvl_2.pop(0)
        
        for i in rayon_lvl_2 : 
            RayonsList.loc[len(RayonsList)] = np.append(tag, np.asarray(i))
            
            
    RayonsList['used'] = [False]*len(RayonsList)

    for i in RayonsList['produit'].squeeze().unique().tolist():
        for t in Settings['KeyRayonSelector']:
            if t.lower() in i.lower():
                RayonsList.loc[RayonsList['produit'] == i, ['used']] = True
        for t in Settings['KeyAvoidSelector']:
            if t.lower() in i.lower():
                RayonsList.loc[RayonsList['produit'] == i, ['used']] = False
    
    return RayonsList



def Recherche(driver:webdriver, lookup):
    rechercheBar = driver.find_element(By.CSS_SELECTOR, Settings['123Click']['rechercheTexte'])
    rechercheBTN = driver.find_element(By.CSS_SELECTOR, Settings['123Click']['rechercheBouton'])
    rechercheBar.clear()
    rechercheBar.send_keys(lookup)
    rechercheBTN.click()
    return  driver.current_url
    

def saveToDoc(tag:str , lieu:LieuxMercuriale, date:datetime, data:pd.DataFrame):
    from daaf.GMS.releve_mercuriale import ReleveMercuriale123Click
    doc = frappe.new_doc('Prix et Marche')
    doc.date = date
    doc.lieu = lieu.get_title()
    doc.rayon = tag

    for row in data['data']:
        row = ReleveMercuriale123Click(row, date, lieu.get_title())
        doc.relevé.append(row.get_doc())

        
    doc.insert(
        ignore_permissions=True, # ignore write permissions during insert
        ignore_links=True, # ignore Link validation in the document
        # ignore_if_duplicate=True, # dont insert if DuplicateEntryError is thrown
        ignore_mandatory=True # insert even if mandatory fields are not set
    )
    
    frappe.db.commit()
    
    return doc

def Haverst(lieu:LieuxMercuriale, users:list[str], driver:webdriver = None, date=datetime.datetime.today()):
    if driver == None : driver = startEngine()
    print('Strat havresting')
    
    link = GetRayonLink(driver)
    # link = link.head(2)
    # logger.debug(link)
    product_List = pd.DataFrame({
            'produit': [],
            'prix_vente': [],
            'poids_de_l_unité_de_vente': [],
            'unite': [],
            'prixUnitaire': [],
            'unité_de_référence': [],
            'origine': [],
            'image': [],
            'bio': [],
            'nutriscore': [],
            'lien': [],
            'tag': [],
        })
        
    doc_list = []

    logger.info('Parcourt des rayons...')
    for index, rayon in link[link['used']].iterrows():
        
        tmp = GetRangeeProduit(driver, rayon['lien'], rayon['produit'] )
        product_List = pd.concat([product_List, tmp], ignore_index=True)
        
        tmp['poids_de_l_unité_de_vente'] = [0]*len(tmp)
        tmp['unité_de_vente'] = [0]*len(tmp)
        tmp['commentaire'] = [""]*len(tmp)
        tmp['prevent_calculation'] = [True]*len(tmp)
        tmp.rename(columns={
            "prixUnitaire": "prix_de_référence", 
            "poids_de_l_unité_de_vente": "poids_de_référence"
            })

        doc = saveToDoc(
            rayon['produit'],
            lieu,
            date,
            loads(tmp.to_json(orient="table"))
        )
        for user in users :
            try:
                frappe.publish_realtime('gms_collecteur')
                frappe.publish_realtime('list_update', doctype="Prix et Marche" )
                notification = frappe.new_doc("Notification Log")
                notification.for_user = user
                notification.set("type", "Alert")
                notification.document_type = 'Prix et Marche'
                notification.document_name = doc
                notification.subject = '<b>GMS : %(lieu)s</b> <br> Rayons lu : %(rayon)s <br> %(produits)s Produits déctecter ' % {
                    'lieu' : lieu.name ,
                    'rayon' : rayon['produit'],
                    'produits' : len(product_List),
                    
                }
                notification.insert()
                frappe.db.commit()
            except Exception:
                logger.error("Failed to send reminder", exc_info=1)   
        
        logger.debug(doc)
        doc_list.append(doc)
        logger.debug('Fin parcourt {}'.format(rayon['produit']))
        
    driver.quit()
    product_List['poids_de_l_unité_de_vente'] = [0]*len(product_List)
    product_List['unité_de_vente'] = [0]*len(product_List)
    product_List['commentaire'] = [""]*len(product_List)
    product_List['prevent_calculation'] = [True]*len(product_List)
    product_List.rename(columns={
        "prixUnitaire": "prix_de_référence", 
        "poids_de_l_unité_de_vente": "poids_de_référence"
        })
    
    
    for user in users :
        try:
            notification = frappe.new_doc("Notification Log")
            notification.for_user = user
            notification.set("type", "Alert")
            notification.document_type = 'Prix et Marche'
            notification.document_name = doc_list[len(doc_list)-1].name
            notification.subject = '<b>FIN - GMS : %(lieu)s</b> <br> Nombre de Rayons lu : %(rayon)s <br> %(produits)s Produits déctecter ' % {
                'lieu' : lieu.name ,
                'rayon' : len(link[link['used']]),
                'produits' : len(product_List),
                
            }
            notification.insert()
            frappe.db.commit()
        except Exception:
            logger.error("Failed to send reminder", exc_info=1)    
    
    frappe.msgprint('FIN - Collect GMS - Test')
    return (
        loads(product_List.to_json(orient="table")),
        doc_list
    )


