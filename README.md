# expreseau_gtfs

![logo](docs/icon.png)

**EXP**loration des **RESEAU**x de transports en commun avec **GTFS**\
Outils pour la manipulation et l'exploration des données gtfs pour l'analyse de la performance des réseaux de transports en commun.

maj : 12/2024 - *modification en cours*
 /!\ ***stade de développement*** /!\

### Classe gtfs_feed:
Le fichier feed.py contient la classe gtfs_feed. 
L'objet gtfs_feed(fichiers *.zip gtfs) permet d'encapsuler le contenu du dossier zippé des GTFS et des les trier selon une date et une heure choisie.

### Classe performances:
L'objet performances contient une séries de fonctions pour analyser la performances de lignes selon plusieurs indicateurs d'offres.

### Classe sections:
Le fichier sections contient la classe sections. L'objet sections() permet de découper les lignes de manière automatisée en fonction de leur variations d'offres.
La fonction sections.decoupe_auto() permet également de détecter les séparations et jonctions de lignes.

### Classe graphes:
L'objet graphe(), permet de convertir à l'aide de la méthode gtfs_to_nx, un objet feed() en graphe Networkx.


### Installation du package :
  1. Dans le dossier ~/expreseau_gtfs/dist récupérer l'archive *.tar.gz
  2. Avec pip : pip install ~/mondossier/*.tar.gz


