# expreseau_gtfs
outils pour la manipulation et l'exploitation des données gtfs pour l'analyse de la performance des réseaux de transports en commun

le fichier analyses.py contient la classe gtfs_feed. L'objet gtfs_feed(fichiers *.zip gtfs) contient une séries de fonctions pour analyser la performances de lignes selon plusieurs indicateurs d'offres.

le fichier sections contient la classe sections. L'objet sections permet de découper les lignes de manière automatisée en fonction de leur variations d'offres. La fonction sections.decoupe_auto() permet également de détecter les séparations et jonctions de lignes.


