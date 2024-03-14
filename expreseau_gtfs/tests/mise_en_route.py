# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 09:18:07 2024

@author: Lucas

tests de mise en route

"""
import sys
# set PYTHONPATH=C:\Users\Lucas\Documents\python_libs_perso\expreseau_gtfs\expreseau_gtfs;%PYTHONPATH%
sys.path.append(r"C:\Users\Lucas\Documents\python_libs_perso\expreseau_gtfs\debug_expreseau_gtfs")
# bibliothèque non packagée /!\ /!\
from debug_expreseau_gtfs.sections import sections
from debug_expreseau_gtfs.analyses import gtfs_feed


import warnings
warnings.filterwarnings('ignore')


# Rétablir le chemin du venv si nécessaire




fic = r"C:\Users\Lucas\Documents\DONNEES\GTFS\saint-etienne\STAS.CACHED_02_2024.GTFS.zip"
gf = gtfs_feed(fic)


f_segments = gf.frequence_par_segment("20240224", [12,14], coords = True)
segments = f_segments[(f_segments.route_short_name=="T3") & (f_segments.direction_id == 1)]


stops = gf.stops
stops.stop_id = stops.stop_id.astype(str)

gs = sections(df = segments)

gda = gs.decoupe_auto(stops = stops, coef = 5)


print(gda[["stop_name_dep", "stop_name_arr"]])

# remove
sys.path.remove(r"C:\Users\Lucas\Documents\python_libs_perso\expreseau_gtfs\debug_expreseau_gtfs")