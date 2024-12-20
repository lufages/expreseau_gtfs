Package expreseau\_gtfs
=======================

EXPloration des RESEAUx de transports en commun avec les fichiers GTFS.

Cette librairie est conçue comme un ensemble d'outils pour la manipulation et l'exploration
des données gtfs pour l'analyse de la performance des réseaux de transports en commun. Elle 
permet également de réaliser des analyses d'accessibilité et du calcul d'itinéraire
basés sur la théorie des graphes.

Auteur : Lucas FAGES

Contact : lucas.fages@cnrs.fr



    

feed
---------------------------
Le module feed la classe gtfs_feed. L'objet gtfs_feed(fichiers *.zip gtfs) 
permet d'encapsuler le contenu du dossier zippé des GTFS et des les trier selon une date et une heure choisie.
Ce module comprend des fonction d'exploration des fichiers GTFS. C'est le point d'entrée pour les autres modules.

.. automodule:: expreseau_gtfs.feed
   :members:
   :undoc-members:
   :show-inheritance:

graphes
------------------------------
L'objet graphe(), permet de convertir à l'aide de la méthode gtfs_to_nx, un objet feed() en graphe Networkx.
Le module graphes contient des fonctionnalités des calculs d'itinéraires, d'isochrones, des closeness et de betweenness centrality.

.. automodule:: expreseau_gtfs.graphes
   :members:
   :undoc-members:
   :show-inheritance:

performances
-----------------------------------

.. automodule:: expreseau_gtfs.performances
   :members:
   :undoc-members:
   :show-inheritance:

sections 
-------------------------------

.. automodule:: expreseau_gtfs.sections
   :members:
   :undoc-members:
   :show-inheritance:

Module utils
----------------------------

.. automodule:: expreseau_gtfs.utils
   :members:
   :undoc-members:
   :show-inheritance:



Quickstart
----------
    QUICKSTART

