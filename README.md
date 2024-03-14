# expreseau_gtfs
**EXP**loration des **RESEAU**x de transports en commun avec **GTFS**\
Outils pour la manipulation et l'exploration des données gtfs pour l'analyse de la performance des réseaux de transports en commun.

maj : 03/2024
version 0.1 encore au /!\ ***stade de développement*** /!\

### Classe gtfs_feed()
Le fichier analyses.py contient la classe gtfs_feed. L'objet gtfs_feed(fichiers *.zip gtfs) contient une séries de fonctions pour analyser la performances de lignes selon plusieurs indicateurs d'offres.
### Classe sections()
Le fichier sections contient la classe sections. L'objet sections() permet de découper les lignes de manière automatisée en fonction de leur variations d'offres.
La fonction sections.decoupe_auto() permet également de détecter les séparations et jonctions de lignes.


### Installation du package :
  1. Dans le dossier ~/expreseau_gtfs/dist récupérer l'archive *.tar.gz
  2. Avec pip : pip install ~/mondossier/*.tar.gz


