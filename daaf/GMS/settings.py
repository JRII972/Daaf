
import os
import yaml
from InquirerPy import inquirer
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException)

# Exception ignorer durant l'attente du webDriver cf documentation
ignored_exceptions = (NoSuchElementException,
                        StaleElementReferenceException,)

# Configuration du script
# Tout ces paramètre non pas à être dans le fichier de configuration, n'y ajouter que les données nécéssaire
defaultSettings = {
    'DEBUG': False,  # Active le Debugage, affichera les étapes des informations sur les étapes encoures. Si faux seul les erreurs critique empechant le dérouler du script seront affiché

    'Proxy': False,  # Pour l'utilisation du Proxy interne de la DAAF Martinique 2023
    'PROXY_HOST': 'rie.proxy.national.agri',  # Rotating proxy or host
    'PROXY_PORT': 8080,  # Proxy port
    'PROXY_USER': None,  # Auth proxy username
    'PROXY_PASS': None,  # Auth proxy password

    # Afficher un encadrement au tour des objets analysé. Utile pour le Debugage
    # Pour améliorer les performances, si vous n'avez pas besoin, désactiver de préférence les Highlights
    # Pour désactiver utiliser
    'Highlights': False,
    # Pour activer :
    # 'Highlights' : {
    #     'color' : 'red', # La couleur
    #     'border' : 5     # La bordure du cadre
    # },


    # Configuration spécifique à Leclerc
    # Voir la documentation pour plus de détaille
    # Si vous n'êtes pas dévelloper NE TOUCHER A AUCUNE DE CES CONFIGURATIONS
    'Leclerc':  {
        # URL de la page d'acceuil
        'BaseURL': "https://fd15-courses.leclercdrive.fr/magasin-974601-le-lamentin.aspx",
        'rechercheTexte': 'inputWRSL301_rechercheTexte',
        'rechercheBouton': 'inputWRSL301_rechercheBouton',
        'ProductScan': {
            'ProduitTag': 'li[class*="Product"]',
            'listProduitsID': "ulListeProduits",
            'information': 'pWCRS310_Info',
            'prixVente': {
                'PartieEntiere': 'PrixUnitairePartieEntiere',
                'PartieDecimale': 'PrixUnitairePartieDecimale',
            },
            'prixUnitairesSTR': 'PrixUniteMesure',
            'Desc': 'Desc',
            'ProduitName': 'Product',
            'Origine': 'Origine',
            'Qualite': ['[class*="Tooltip_QUALITE"]', '[class*="ContenuTooltip"] > strong '],
            'NutriScore': '[data-typesticker="NUTRISCORE"]',
            'image': 'Content',
        },
    },
    '123Click':  {
        # URL de la page d'acceuil
        'BaseURL': "https://martinique.123-click.com/",
        'rechercheTexte': 'input[class="rechercher"]', # Classe 
        'rechercheBouton': 'div[class="btn-search btn btn-top"]',
        'ProductScan': {
            'unite' : 'poids-suffixe-holder',
            'ProduitTag': 'div[class*="product-list-affichage-desktop"]',
            'listProduitsID': 'div[class*="product_list"]',
            'information': 'pWCRS310_Info',
            'prixVente': 'price-full',
            'prixUnitairesSTR': 'unity-price',
            'Desc': 'Desc',
            'ProduitName': 'div.product-descri > div.desc > a',
            'Origine': 'Origine',
            'Qualite': ['[class*="Tooltip_QUALITE"]', '[class*="ContenuTooltip"] > strong '],
            'NutriScore': 'div.picto-item.nutri-score-item > img',
            'image': 'a.image > img.owl-lazy',
        },
    },

    # Donnée de filtrage des rayons
    'KeyRayonSelector': [
        'bio',
        'frais',
        'viande',
        'poisson',
        'Fruit',
        'Légume'
    ],
    # Donnée de filtrage des rangée
    'KeyRangéeSelector': [
        'frais',
        'viande',
        'poisson',
        'Fruit',
        'Légume'
    ],
    'KeyAvoidSelector': [
        'Chat',
        'Chien'
    ],

    # Unité detectable et mappage
    'unite': {
        'KG': 'KG',
        'G': 'G',
        'L': 'L',
        'ML': 'ML',
    }

}

try:
    with open(os.path.join(os.getcwd(),"GMS_config.yaml"), 'r+') as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)
        config = defaultSettings if config is None else config

        Settings = defaultSettings
        Settings.update(config)

except:
    with open("../GMS_config.yaml", 'w') as yamlfile:
        Settings = defaultSettings
        
if (Settings['Proxy']) : 
            if (type(Settings['PROXY_USER']) != str) | (type(Settings['PROXY_PASS']) != str) :
                Settings['PROXY_USER'] = inquirer.text(
                    message="Identifiant proxy"
                ).execute()
                Settings['PROXY_PASS'] = inquirer.secret(
                    message="Mot de passe proxy"
                ).execute()