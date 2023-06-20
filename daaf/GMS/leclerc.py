import os, re
import time
from InquirerPy.validator import PathValidator

from daaf.GMS.settings import ignored_exceptions, Settings
from daaf.GMS.scrapper import get_driver, highlight, detectUnite
from datetime import date

import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

# ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

import frappe 
frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("sisep", allow_site=True, file_count=50)

# ### Fonction du module Leclerc et co pour détection et recolte


# Detect si le produit récolter est viable
# TODO : Non implémenter : Ajouter les conditions de validation
# Lever un erreur dans le cas ou le produit n'est pas bon
# Cela bloquera l'enregistrement du produit, affichera une information pour le degugage, et passera au suivant


def dateEnhance(prixVente: float, prixUnitaire: float, unitePrixUnitaire: str, Poids: float, uniteVente: str) -> tuple:
    if (prixVente == None) & (prixUnitaire != None) & (unitePrixUnitaire != None) & (Poids != None) & (uniteVente != None):
        print("Not Implemented")

    return prixVente, prixUnitaire, Poids


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
    int:NutriScore

    """

    if Settings['Highlights']:
        parent = produit._parent

        def apply_style(s):
            parent.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                  produit, s)
        original_style = produit.get_attribute('style')
        actions = ActionChains(driver)
        actions.move_to_element(produit).perform()
        apply_style("border: {0}px solid {1};".format(
            Settings['Highlights']['border'], Settings['Highlights']['color']))

    # Disponibilité
    try:
        information = produit.find_element(
            By.CLASS_NAME, "pWCRS310_Info").get_attribute("innerHTML").rstrip().lstrip()
    except:
        information = None

    # Prix de vente
    try:
        prixVente = int(produit.find_element(By.CSS_SELECTOR, '[class*="PrixUnitairePartieEntiere"]').get_attribute("innerHTML").rstrip().lstrip()) + \
            int(produit.find_element(By.CSS_SELECTOR, '[class*="PrixUnitairePartieDecimale"]').get_attribute(
                "innerHTML").rstrip().lstrip().replace(',', '')) / 100
    except:
        prixVente = None

    # Prix unitaire
    try:
        prixUnitairesSTR = produit.find_element(
            By.CSS_SELECTOR, '[class*="PrixUniteMesure"]').get_attribute("innerHTML")
        prixUnitaire = float(
            prixUnitairesSTR[:prixUnitairesSTR.find('€')].replace(',', '.'))
        unitePrixUnitaire = prixUnitairesSTR[prixUnitairesSTR.find(
            '/')+1:].rstrip().lstrip()
    except:
        prixUnitaire = None
        unitePrixUnitaire = None

    # Produit
    try:
        Desc = produit.find_element(By.CSS_SELECTOR, '[class*="Desc"]')
        ProduitName = Desc.find_element(
            By.CSS_SELECTOR, '[class*="Product"]').get_attribute("innerHTML").rstrip().lstrip()
        Poids = ProduitName[ProduitName.find('<br>')+4:].rstrip().lstrip()
        # document.querySelectorAll('[src*="VisuelEchelle"]')
        uniteVente = detectUnite(Poids)
        Poids = float(re.sub('\D', '', Poids).replace(',', ''))

        ProduitName = ProduitName[:ProduitName.find(
            '<br>')].rstrip().lstrip().replace('<br>', '')
    except Exception as e:
        # print(e)
        Poids = None
        ProduitName = None

    # Origine
    try:
        Origine = produit.find_element(
            By.CSS_SELECTOR, '[class*="Origine"]').get_attribute("innerHTML").rstrip().lstrip()
    except:
        Origine = None

    # Image
    try:
        image = produit.find_element(
            By.CSS_SELECTOR, '[class*="Content"]').find_element(By.TAG_NAME, "img").get_attribute('src')
        # Image(url = image)
    except:
        image = None

    # QUALITE
    try:
        Qualite = produit.find_element(By.CSS_SELECTOR, '[class*="Tooltip_QUALITE"]').find_element(
            By.CSS_SELECTOR, '[class*="ContenuTooltip"] > strong ').get_attribute('innerHTML')

    except:
        Qualite = None

    # NutriScore
    try:
        NutriScore = produit.find_element(
            By.CSS_SELECTOR, '[data-typesticker="NUTRISCORE"]').get_attribute('src')

        if (NutriScore == "https://fd15-photos.leclercdrive.fr/image.ashx?id=1237710&use=nsc&cat=p&typeid=i&mindim=35"):
            NutriScore = 'E'
        elif (NutriScore == "https://fd15-photos.leclercdrive.fr/image.ashx?id=1237709&use=nsc&cat=p&typeid=i&mindim=35"):
            NutriScore = 'D'
        elif (NutriScore == "https://fd15-photos.leclercdrive.fr/image.ashx?id=1237708&use=nsc&cat=p&typeid=i&mindim=35"):
            NutriScore = 'C'
        elif (NutriScore == "https://fd15-photos.leclercdrive.fr/image.ashx?id=1237707&use=nsc&cat=p&typeid=i&mindim=35"):
            NutriScore = 'B'
        elif (NutriScore == "https://fd15-photos.leclercdrive.fr/image.ashx?id=1237706&use=nsc&cat=p&typeid=i&mindim=35"):
            NutriScore = 'A'
        elif (NutriScore == "https://fd15-photos.leclercdrive.fr/image.ashx?id=2389083&use=nsc&cat=p&typeid=i&mindim=35"):
            NutriScore = 'NC'

    except:
        NutriScore = None

    prixVente, prixUnitaire, Poids = dateEnhance(
        prixVente, prixUnitaire, unitePrixUnitaire, Poids, uniteVente)

    if Settings['Highlights']:
        apply_style(original_style)
    return ProduitName, prixVente, Poids, uniteVente, prixUnitaire, unitePrixUnitaire, Origine, information, image, Qualite, NutriScore


def GetRangeeProduit(driver:webdriver, rayon, tag):
    driver.get(rayon)

    # rayons = driver.find_element(By.CSS_SELECTOR, '[class*="FiltresNavigation"]')
    # list_rayons = {}

    # for i in rayons.find_elements(By.TAG_NAME, "A") :
    #     if i.get_attribute('innerHTML').strip().upper() != "TOUS" :
    #         list_rayons[i.get_attribute('innerHTML').strip()] = i.get_attribute('href')

    product_List = pd.DataFrame({
        'nom': [],
        'prix': [],
        'poids': [],
        'unite': [],
        'prixUnitaire': [],
        'unitePrixUnitaire': [],
        'Origine': [],
        'information': [],
        'image': [],
        'Qualite': [],
        'NutriScore': [],
        'tag': []
    })

    
    #     RayonLoop = progress.add_task("[red]Parcourt des rayon...", total=len(list_rayons))
    #     for tag, link  in list_rayons.items() :
    # driver.get(link)
    # if tag == "" :
    #     tag = driver.find_element(By.CSS_SELECTOR, '[class*="FiltreActif"]').find_element(By.TAG_NAME, 'A').get_attribute('innerHTML').rstrip().lstrip()
    FIRST_ELT = None

    listProduits = WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
        .until(expected_conditions.presence_of_element_located((By.ID, Settings['Leclerc']['ProductScan']['listProduitsID']))) \
        .find_elements(By.CSS_SELECTOR, Settings['Leclerc']['ProductScan']['ProduitTag'])

    print(f'{len(listProduits)} produits potentiel - {tag}: lecture ...')
    for i in range(4, len(listProduits) + 4):
        try:
            getProduit(driver, driver.find_element(By.ID, f'sId{i}'))
        except:
            continue

        FIRST_ELT = i
        break

    if (FIRST_ELT == None):
        FIRST_ELT = 4

    logger.info(f"[green]Rangé : {tag}... {len(listProduits)} produits")
    lenRangé = len(listProduits)
    for i in range(FIRST_ELT, len(listProduits) + FIRST_ELT):
        try:
            product_List.loc[len(product_List)] = np.append(np.asarray(
                getProduit(driver, driver.find_element(By.ID, f'sId{i}'))), tag)
        except Exception as e:
            logger.debug(
                f'[bold blue]Erreur n°{i} : {e.__cause__}')
            continue

    logger.info(f'{len(product_List)} produits lu sur {len(listProduits)} - {tag}')

    return product_List
# result = GetRayon(rayon)



def getCatRayons(driver:webdriver):
    driver.get(Settings['Leclerc']['BaseURL'])
    
    logger.info(
        "GMS - LECLERC : recherche des rayons...")
    RayonsList = pd.DataFrame({
        'cat': [],
        'nom': [],
        'lien': [],
        'image': [],
    })

    WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
        .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'a[class*="js-ouvreRayons"]'))).click()
    listRayons = WebDriverWait(driver, 15, ignored_exceptions=ignored_exceptions) \
        .until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, 'li[class="rayon-droite"]')))

    logger.info("GMS - LECLERC : Lecture des rayons")
    for i in listRayons:
        cat = i.find_element(
            By.CSS_SELECTOR, 'div[class="rayon-droite-titre"]').get_attribute("innerText")
        subRayon = i.find_elements(By.CSS_SELECTOR, 'li[class="famille"]')
        if Settings['DEBUG'] :
            logger.info(f'GMS - LECLERC : Rayon : {cat} avec {len(subRayon)} éléments')

        for j in subRayon:
            RayonsList.loc[len(RayonsList)] = [
                cat,
                j.find_element(By.TAG_NAME, 'SPAN').get_attribute(
                    "innerText"),
                j.find_element(By.TAG_NAME, 'a').get_attribute("href"),
                j.find_element(By.TAG_NAME, 'img').get_attribute("src")
            ]

    RayonsList['used'] = [False]*len(RayonsList)

    KeyRayonSelector = [
        'bio',
        'frais',
        'viande',
        'poisson',
        'Fruit',
        'Légume'
    ]

    for i in RayonsList['cat'].squeeze().unique().tolist():
        for t in KeyRayonSelector:
            if t in i.lower():
                RayonsList.loc[RayonsList['cat'] == i, ['used']] = True

    # RayonsList.loc[RayonsList['used']]

    return RayonsList


def GetRayonLink(driver:webdriver, RayonsList: pd.DataFrame = None):
    if type(RayonsList) != pd.DataFrame: RayonsList = getCatRayons(driver)
        
    logger.info(f'GMS - LECLERC : Recherche des rayons... {len(RayonsList)}')
    list_rayons = pd.DataFrame({
        'cat': [],
        'nom': [],
        'lien': []
    })
    
    for index, rayon in RayonsList.iterrows():
        try :
            logger.debug(f'GMS - LECLERC : Lecture {rayon["cat"]}')
            driver.get(rayon['lien'])

            rayons = driver.find_element(
                By.CSS_SELECTOR, '[class*="FiltresNavigation"]')

            for i in rayons.find_elements(By.TAG_NAME, "A"):
                if i.get_attribute('innerHTML').strip().upper() != "TOUS":
                    list_rayons.loc[len(list_rayons)] = [
                        rayon['cat'],
                        i.get_attribute('innerHTML').strip(),
                        i.get_attribute('href')
                    ]
            
        except : 
            list_rayons.loc[len(list_rayons)] = [
                        rayon['cat'],
                        rayon['cat'],
                        rayon['lien']
                    ]
            
            

    list_rayons['used'] = [False]*len(list_rayons)

    for i in list_rayons['nom'].squeeze().unique().tolist():
        for t in Settings['KeyRayonSelector']:
            if t in i.lower():
                list_rayons.loc[list_rayons['nom'] == i, ['used']] = True

    # list_rayons.loc[list_rayons['used']]

    return list_rayons

def Recherche(driver:webdriver, lookup):
    rechercheBar = driver.find_element(By.ID, Settings['Leclerc']['rechercheTexte'])
    rechercheBTN = driver.find_element(By.ID, Settings['Leclerc']['rechercheBouton'])
    rechercheBar.clear()
    rechercheBar.send_keys(lookup)
    rechercheBTN.click()
    return  driver.current_url
    

def Havrest(driver:webdriver = None): 
    if driver == None : driver = get_driver()
    list_rayons = GetRayonLink(driver).head(1)
    product_List = pd.DataFrame({
        'nom': [],
        'prix': [],
        'poids': [],
        'unite': [],
        'prixUnitaire': [],
        'unitePrixUnitaire': [],
        'Origine': [],
        'information': [],
        'image': [],
        'Qualite': [],
        'tag': []
    })
    for index, rayon in list_rayons.iterrows():
        # Deprecated but still work
        # product_List = product_List.append(
        #     GetRangeeProduit(driver, rayon['lien'], rayon['cat'])
        # )
        product_List = pd.concat([product_List, GetRangeeProduit(driver, rayon['lien'], rayon['cat'])], ignore_index=True)
        
    return product_List