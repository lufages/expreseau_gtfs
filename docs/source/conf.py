# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

# include_html.append('include_html')
project = "Expreseau GTFS"
copyright = '2024, Lucas FAGES'
author = 'Lucas FAGES'
# master_doc = 'modules'
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

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']  # Vous pouvez exclure certains fichiers ou répertoires si nécessaire
# import sphinx_pdj_theme
html_theme = 'sphinx_rtd_theme'

# Répertoire pour les fichiers statiques (images, CSS, etc.)
html_static_path = ['_static']   


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
