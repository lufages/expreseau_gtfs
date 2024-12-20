# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 10:11:31 2024

@author: Lucas
"""
import sys
# set PYTHONPATH=C:\Users\Lucas\Documents\python_libs_perso\expreseau_gtfs\expreseau_gtfs;%PYTHONPATH%
# sys.path.append(r"C:\Users\Lucas\Documents\python_libs_perso\expreseau_gtfs\expreseau_gtfs")


from expreseau_gtfs.analyses import gtfs_feed
from expreseau_gtfs.graphes import graphes

fic = r"gtfs.zip"

gf = gtfs_feed(fic)

graphe = graphes(gf = gf, date = "20240124", plage_horaire = [7,9])

g = graphe.gtfs_to_nx(verbose = True)


# remove
# sys.path.remove(r"C:\Users\Lucas\Documents\python_libs_perso\expreseau_gtfs\expreseau_gtfs")