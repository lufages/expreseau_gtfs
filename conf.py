# -- Path setup --------------------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('expreseau_gtfs'))  # Ajouter le répertoire contenant votre code source

# -- Project information -----------------------------------------------------
project = 'Expreseau GTFS'
author = 'Lucas FAGES'
release = '1.0.0'  # Version de votre projet

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',        # Pour générer la documentation à partir des docstrings
    'sphinx.ext.napoleon',       # Pour le support des formats Google et NumPy docstrings
    'sphinx.ext.viewcode',       # Pour générer des liens vers le code source dans la doc
    'sphinx.ext.intersphinx',    # Pour lier à la documentation d'autres projets
    # 'sphinx_rtd_theme',          # Thème Read the Docs
]

templates_path = ['_templates']
exclude_patterns = []  # Vous pouvez exclure certains fichiers ou répertoires si nécessaire

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'  # Utilisation du thème Read the Docs
html_static_path = ['_static']    # Répertoire pour les fichiers statiques (images, CSS, etc.)

# -- Options for autodoc -----------------------------------------------------
autodoc_default_flags = ['members', 'undoc-members', 'show-inheritance']  # Gérer la documentation des membres de classe, etc.

# -- Options for Napoleon extension ----------------------------------------
napoleon_google_docstring = True   # Support des docstrings au format Google
napoleon_numpy_docstring = True    # Support des docstrings au format NumPy

# -- Intersphinx configuration ------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),  # Lien vers la documentation Python
}

# -- Options for todo extension ---------------------------------------------
todo_include_todos = True  # Inclure les tâches TODO dans la documentation

# -- Additional options ------------------------------------------------------
# D'autres configurations peuvent être ajoutées selon les besoins spécifiques de votre projet.
