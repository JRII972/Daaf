import os
import io
import re
import requests
import pytesseract
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
from daaf.GMS.scrapper import get_driver #, highlight
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

def startEngine(driver:webdriver = get_driver()):

    driver.get('https://martinique.123-click.com/')

    # cookies / onetrust
    try : 
        # driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        WebDriverWait( driver, 30, ignored_exceptions=ignored_exceptions) \
                .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'a[class="cookie_btn_main accept"]'))).click()
    except : 
        print("trust already accept")
        
    return driver


# Non utilisée
def detectUnite(str: str):
    for u, val in Settings['unite'].items():
        if re.sub(r'[0-9]+', '', str).replace(" ", "").upper()[:2] == u:
            return val

    return None

# Detect si le produit récolter est viable
# TODO : Non implémenter : Ajouter les conditions de validation
# Lever un erreur dans le cas ou le produit n'est pas bon
# Cela bloquera l'enregistrement du produit, affichera une information pour le degugage, et passera au suivant


def dateEnhance(ProduitName:str ,prixVente: float, prixUnitaire: float, unitePrixUnitaire: str, Poids: float, uniteVente: str) -> tuple:
    try : 
        
        if (prixVente == None) & (prixUnitaire != None) & (unitePrixUnitaire != None) & (Poids != None) & (uniteVente != None):
            print("Not Implemented")


        if ('Œuf'.lower() in ProduitName.lower()) | ('oeufs' in ProduitName.lower()) & (uniteVente == 'unitaire'):
            if (prixVente == None) & (prixUnitaire != None) : 
                prixVente = prixUnitaire
            print(prixVente, Poids )
            prixUnitaire = prixVente / Poids
            unitePrixUnitaire = 'unitaire'
            
    except Exception as e :
        print(e)
    
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

    except:
        prixUnitaire = None
        unitePrixUnitaire = None

    
        
    # Poids
    try:
        Poids = float(re.search(r'\d+', produit.find_element(By.CSS_SELECTOR, 'div[class*="poids-suffixe-holder"]').get_attribute("innerHTML")).group())
    except Exception as e:
        # print(e)
        Poids = None
        
    # uniteVente
    try:
        uniteVente = re.search(r'[a-zA-Z]+', produit.find_element(By.CSS_SELECTOR, 'div[class*="poids-suffixe-holder"]').get_attribute("innerHTML")).group()
        uniteVente = 'unitaire' if uniteVente.lower() == 'x' else uniteVente
    except Exception as e:
        # print(e)
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
        # Image(url = image)
    except:
        image = None

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

    return ProduitName, prixVente, Poids, uniteVente, prixUnitaire, unitePrixUnitaire, Origine, image, bio, Nutriscore




def GetRangeeProduit(driver:webdriver, rayon, tag, progress = Progress()):
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
        'tag': []
    })
    
    product_List["bio"]=product_List["bio"].astype(bool)

    listProduits = WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
        .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="product_list"]')))
    Rangé = progress.add_task(f"[green]Havresting : {tag}...", total=None)
    
    while True:
        try :
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            produit = WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
        .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="product-list-affichage-desktop"]')))
            
            if Settings['DEBUG'] : driver.execute_script("window.scrollTo(0, 0);")
            
            product_List.loc[len(product_List)] = np.append(np.asarray(getProduit(driver, produit)), tag)
            
            
            driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, produit)
        except Exception as e : 
            print(e)
            break    

    print(f'{len(product_List)} produits lu - {tag}')
    progress.remove_task(Rangé)

    return product_List



def GetRayonLink(driver:webdriver) -> pd.DataFrame:
    driver.get(Settings['123Click']['BaseURL'])

    with Progress() as progress:
        SubRayonLoop = progress.add_task(
                "[red]Recherche des rayons...", total=None)
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
        progress.update(SubRayonLoop, total=len(rayon_lvl_1))
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
                
            progress.update(SubRayonLoop, advance=1)
                
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
    



def Haverst(driver:webdriver = startEngine()):
    
    link = GetRayonLink(driver)

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
            'tag': []
        })

    with Progress() as progress:
        SubRayonLoop = progress.add_task(
                    "[red]Parcourt des rayons...", total=len(link['used']))
        for index, rayon in link[link['used']].iterrows():
            
            product_List = pd.concat([product_List, GetRangeeProduit(driver, rayon['lien'], rayon['produit'], progress )], ignore_index=True)
            progress.update(SubRayonLoop, advance=1)
        
    driver.quit()

    print(product_List)
    
    product_List.rename(columns={
        "prixUnitaire": "prix_de_référence", 
        "poids_de_l_unité_de_vente": "poids_de_référence"
        })
    
    product_List['poids_de_l_unité_de_vente'] = [0]*len(product_List)
    product_List['unité_de_vente'] = [0]*len(product_List)
    product_List['commentaire'] = [""]*len(product_List)
    product_List['prevent_calculation'] = [True]*len(product_List)
    
    return loads(product_List.to_json(orient="table"))


