# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

# include_html.append('include_html')
project = "Expreseau GTFS"
copyright = '2024, Lucas FAGES'
author = 'Lucas FAGES'
master_doc = 'modules'
# -- Project information -----------------------------------------------------

release = '1.0.0'  # Version de votre projet

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',        # Pour générer la documentation à partir des docstrings
    'sphinx.ext.napoleon',       # Pour le support des formats Google et NumPy docstrings
    'sphinx.ext.viewcode',       # Pour générer des liens vers le code source dans la doc
    'sphinx.ext.intersphinx',
"myst_parser"    # Pour lier à la documentation d'autres projets
    # 'sphinx_rtd_theme',          # Thème Read the Docs
]
extensions.append('include_html')
# extensions.append('html_toc')

templates_path = ['_templates']
exclude_patterns = []  # Vous pouvez exclure certains fichiers ou répertoires si nécessaire
# import sphinx_pdj_theme
html_theme = 'sphinx_rtd_theme'
# html_theme_path = [sphinx_pdj_theme.get_html_theme_path()]
# -- Options for HTML output -------------------------------------------------
# html_theme = 'pdj'  # Utilisation du thème Read the Docs
html_static_path = ['_static']    # Répertoire pour les fichiers statiques (images, CSS, etc.)
# html_extra_path = [r"C:\Users\Lucas\Documents\python_libs_perso\expreseau_gtfs\expreseau_gtfs\build\html\html_extra\QUICKSTART.html"]
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

autodoc_default_options = {
    'members': True,            # Documente les classes/fonctions/méthodes
    'undoc-members': True,      # Inclut même les membres non documentés
    # 'private-members': True,    # Inclut les membres privés (_nom)
    # 'special-members': '__init__',  # Inclut les membres spéciaux
    'show-inheritance': True,   # Affiche les informations d'héritage
}
