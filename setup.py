from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in daaf/__init__.py
from daaf import __version__ as version

setup(
	name="daaf",
	version=version,
	description="Module de base pour la gestion des données interne",
	author="SISEP - DAAF",
	author_email="jeremyjovinac@hotmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
