import pandas as pd
import numpy as np
from shapely import Point, LineString
import geopandas as gpd
from expreseau_gtfs.utils import seconds_to_hms
from expreseau_gtfs.feed import gtfs_feed

class performances:    
    
    def __init__(self, Feed):
        
        self._Feed = Feed
    
    
    def frequence_par_ligne(self, stop_sequence = 1):
        """
        Renvoit la fréquence moyenne par ligne sur la période renseignée dans 
        l'objet gtfs_feed.
        
        Parameters
        ----------
        stop_sequence : int, optional
            Détermine à quel numéro d'arrêt de la ligne sera 
            calculée la fréquence moyenne. Par défaut, stop_sequence = 1.

        Returns
        -------
        pandas.dataframe()
            Dataframe avec la fréquence par ligne et le temps 
            d'attente moyen.

        """
        return self._get_frequence_par_ligne(stop_sequence)
    

    def amplitude_par_ligne(self):
        """
        Renvoit un dataframe contenant l'heure du premier départ et l'heure de
        la dernière arrivée par ligne.        

        Returns
        -------
        pandas.dataframe()
            Dataframe de l'amplitude par ligne.
        """
        return self._get_amplitude_par_ligne()

    
    def frequence_par_segment(self, coords = False):
        """
        Renvoit la fréquence moyenne par segments sur la période renseignée dans 
        l'objet gtfs_feed.        

        Parameters
        ----------
        coords : bool, optional
            Permet d'avoir les coordonnées des segments pour
            un post-traitement avec la classe sections. Par défaut, coords = False.

        Returns
        -------
        geopandas.geodataframe()
            Fréquence par segment (arrêt à arrêt) et par ligne.

        """
        return self._get_frequence_par_segment(coords)
    
    def traces_des_lignes(self):
        """
        Renvoit un geodataframe des tracés des lignes.

        Returns
        -------
        geopandas.geodataframe()
            Geodataframe des formes des lignes (shapes.txt) avec le trip_id associé.

        """
        return self._get_trace_des_lignes()

    
    def frequence_par_shapes(self, stop_sequence = 1):
        """
        Renvoit la fréquence moyenne par shape sur la période renseignée dans 
        l'objet gtfs_feed.        

        Parameters
        ----------
        stop_sequence : int, optional
            Détermine à quel numéro d'arrêt de la ligne sera 
            calculée la fréquence moyenne. Par défaut, stop_sequence = 1

        Returns
        -------
        pandas.dataframe()
            Dataframe de la fréquence par shape_id.

        """
        return self._get_frequence_par_shape(stop_sequence)


    def freq_min(self, stop_sequence = 8):
        """
        Pour chaque ligne, calcul de la fréquence moyenne par heure de 7h à 21h.
        On récupère la plus mauvaise de ces fréquences pour chauque ligne.

        Parameters
        ----------
        stop_sequence : int, optional
            Par défaut stop_sequence = 8.

        Returns
        -------
       pandas.dataframe()
           Dataframe de la fréquence par minimale.

        """
        return self._get_freq_min(stop_sequence)

# =============================================================================
# ########## getters  
# 
# =============================================================================

    def _get_freq_min(self, stop_sequence):
        
        plage_horaire=[7, 21]
        
        # on créé un autre feed sur la base du premier pour élargir les horaires
        feed_temp = gtfs_feed(self._Feed.gtfs_path,
                              date=self._Feed.date,
                              plage_horaire=plage_horaire,
                              methode = self._Feed.methode)
        
        
        # il faut calculer la fréquence par heure de 7h à 21h par ligne
        # recupère la table horaire avec les services circulant le jour demandé entre 7h et 21h (par défaut)
        trips_stops = feed_temp.table_horaire()
        # selection des colonnes :
        trips_stops = trips_stops[["arrival_time",'route_id','route_short_name', 'trip_id',
                    'direction_id', 'service_id', "stop_sequence", 'stop_id']]
        # on découpe les "arrival_time" en tranches horaires de 1h
        trips_stops['arrival_time_'] = \
        pd.cut(x=trips_stops['arrival_time'] / 3600, bins=np.arange(plage_horaire[0],
                                                                    plage_horaire[1]))
        # selection des colonnes
        trips_stops = trips_stops[['route_short_name','direction_id', 
                                   'arrival_time_', "stop_sequence"]]
        # selection d'un arret via le stop_sequence (5 par défaut)
        trips_stops_ = trips_stops[trips_stops.stop_sequence == stop_sequence]
        # on compte le nombre de passage par arret par ligne par direction :
        trips_stops_ = trips_stops_\
            .value_counts(["route_short_name","direction_id","arrival_time_"]).reset_index()
        # conversion du nombre de passages en fréquences horaires

        trips_stops_["freq"] = 60 / trips_stops_['count']
        #pour chaque ligne, on regarde sur quelle tranche horaire la fréquence
        # est la plus mauvaise :
        # instacie liste vide :
        liste_min_freq = list() 
        # bouclage
        for rt in trips_stops_.route_short_name.unique():
            tmp = trips_stops_[trips_stops_.route_short_name == rt]
            liste_min_freq.append(max(tmp.freq.values))
        # enregistrement dans un pandas dataframe :
        df = pd.DataFrame((trips_stops_.route_short_name.unique(), liste_min_freq)).T
        df.columns = ['route_short_name', "frequence min"]
        return df

 
    def _get_frequence_par_segment(self, coords):
    
        stops = self._Feed.stops
        # extraction de la table horaire :
        table = self._Feed.table_horaire()
        # on réordonne la table par trips et par ordre croissant de stop_sequence
        table.sort_values(by=['trip_id', 'stop_sequence'], inplace=True)
        table = table.reset_index(drop=True)
        # je convertis les stop_id en string pour la fusion :
        table["stop_id"] = table["stop_id"].astype(str)
        # on créé un décalage d'un arrêt pour chaque trips pour avoir les 
        # deux poitns d'un segment (arret à arret) :
        table['end_stop_id'] = table.groupby(["trip_id"])[['stop_id']].shift(-1)
        # # nettoyage  des colonnes :
        table.drop(columns=['route_id',  'service_id'], inplace = True)
        table = table[["trip_id","route_short_name","direction_id",
                       "arrival_time","departure_time","stop_sequence",
                       "stop_id","end_stop_id"]]
        table.sort_values(by=['trip_id', 'stop_sequence'], inplace=True)
        
        
        # Ici, on supprime les arrêts décalé de -1 (shift) qui ont la valeur Nan
        # il s'agit en fait d'un arret de fin pour le trip concerné par le shift
        # on ne peut donc pas créer de segment et donc je le supprime.
        # Au passage on enregistre ces résultats dans un df appelé fréquence :
        frequence = table.dropna(subset="end_stop_id") #fillna('fin')
        # On créé les segments en regroupant l'id du stop courant avec le courant + 1 :
        frequence["segment"] = frequence['stop_id'].astype(str)+ \
            ' - ' + frequence['end_stop_id'].astype(str)
        
        stops.stop_id = stops.stop_id.astype(str)
        # on fusionne pour récupérer les coordonnées des arrêts :
        frequence = frequence.merge(stops[['stop_id', 'stop_lat', 'stop_lon']], on = "stop_id")
        frequence = frequence.merge(stops[['stop_id', 'stop_lat', 'stop_lon']],
                                    left_on = "end_stop_id",
                                    right_on='stop_id',
                                    suffixes = ('_dep','_arr'))
        
        # On groupe pour avoir le nombre de service passant par ligne sur 
        # chaque segment : 
        table_frequences = frequence[['segment', "route_short_name",
                                      'direction_id', "trip_id","stop_id_dep",
                                      "stop_lon_dep", "stop_lat_dep",
                                     "stop_id_arr", "stop_lon_arr", "stop_lat_arr"]]\
                        .groupby(['segment', "route_short_name", 'direction_id',
                                  "stop_id_dep", "stop_lon_dep", "stop_lat_dep",
                                     "stop_id_arr", "stop_lon_arr", "stop_lat_arr"])\
                        .count().reset_index()
        # conversion des segments en géométries linestrings :
        liste_segments = list()
        for idx in table_frequences.index:
            # on recupere les coordonnees :
            lonx = table_frequences.iloc[idx].stop_lon_dep
            latx = table_frequences.iloc[idx].stop_lat_dep
            lony = table_frequences.iloc[idx].stop_lon_arr
            laty = table_frequences.iloc[idx].stop_lat_arr
            # on convertit les points en geometrie et on stocke dans une liste de lignes
            liste_segments.append(LineString([Point([lonx, latx]),
                                              Point([lony, laty])]))
        if coords == True:
            segments_freq = gpd.GeoDataFrame(
                table_frequences[["segment", "route_short_name", "direction_id",
                                  "trip_id", "stop_lon_dep", "stop_lat_dep",
                                  "stop_lon_arr", "stop_lat_arr"]],
                geometry = gpd.GeoSeries(liste_segments).set_crs('epsg:4326'))
        else:
            # on créé un gdf segments_freq
            segments_freq = gpd.GeoDataFrame(
                table_frequences[["segment", "route_short_name", "direction_id", "trip_id"]],
                geometry = gpd.GeoSeries(liste_segments).set_crs('epsg:4326'))
        # on renomme trips_id en nbtrips :
        segments_freq = segments_freq.rename(columns = { "trip_id":"nbtrips"})
        return segments_freq
    
    def _get_frequence_par_ligne(self, stop_sequence):
        
        plage_horaire = self._Feed.plage_horaire
        routes = self._Feed.routes
        #table horaire :
        trips_stops = self._Feed.table_horaire()
        trips_stops = trips_stops[['route_id','route_short_name', 'trip_id',
                    'direction_id', 'service_id', "stop_sequence", 'stop_id']]
        
        # on merge avec la route pour avoir le numéro :
        trips_stops = trips_stops.merge(routes[["route_id", "route_long_name"]],
                                        on = "route_id", how="right")
        
        # on créé un df freq_trips
        # on trie sur la stop_sequence 5
        freq_trips = trips_stops[trips_stops.stop_sequence == stop_sequence] 
        # on ne garde que ces colonnes :
        freq_trips = freq_trips[['route_id','route_short_name',
                                 'trip_id', 'direction_id', 'service_id']]
        # table de contingence pour avoir la fréquence par trip :
        freq_trips = freq_trips.pivot_table('trip_id', 
                                            ['direction_id', 'route_short_name'],
                                            aggfunc='count').reset_index()
        
        # renomme les colonnes : 
        freq_trips = freq_trips[["route_short_name","direction_id", "trip_id"]]
        freq_trips.columns = ["route_short_name","direction_id", "nbtrips"]
        #calcule la frequence moyenne :
        freq_trips['mean_headway'] = \
            ((plage_horaire[1] - plage_horaire[0]) * 60) / freq_trips.nbtrips

        return freq_trips
        
    def _get_frequence_par_shape(self, stop_sequence):
        
        if not self._Feed.shapes.empty:

            plage_horaire = self._Feed.plage_horaire
            
            routes = self._Feed.routes
            
            # on appelle la table horaire :
            trips_stops = self._Feed.table_horaire()
            trips_stops = trips_stops[['shape_id','route_id', 'route_short_name',
            'trip_id','direction_id', 'service_id', "stop_sequence", 'stop_id']]
            
            # on merge avec la route pour avoir le numéro :
            trips_stops = trips_stops.merge(routes[["route_id", "route_long_name"]],
                                            on = "route_id")
            
            # on créé un df freq_trips
            # on trie sur la stop_sequence 5
            freq_trips_shapes = trips_stops[trips_stops.stop_sequence == stop_sequence] 
            # on ne garde que ces colonnes :
            freq_trips_shapes = freq_trips_shapes[['shape_id','route_short_name',
                                     'trip_id', 'direction_id', 'service_id']]
            # table de contingence pour avoir la fréquence par trip :
            freq_trips_shapes = freq_trips_shapes.pivot_table('trip_id', 
                                                ['direction_id', 'shape_id', 'route_short_name'],
                                                aggfunc='count').reset_index()
            
            # renomme les colonnes : 
            freq_trips_shapes = freq_trips_shapes[["shape_id", 'route_short_name',"direction_id", "trip_id"]]
            freq_trips_shapes.columns = ["shape_id", 'route_short_name',"direction_id", "nbtrips"]
            #calcule la frequence moyenne :
            freq_trips_shapes['mean_headway'] = \
                ((plage_horaire[1] - plage_horaire[0]) * 60) / freq_trips_shapes.nbtrips

            return freq_trips_shapes
        else:
            print("Pas de fichier shapes.txt")
            return pd.DataFrame([])
    
    
    def _get_amplitude_par_ligne(self):
        
        plage_horaire = [0, 25]
        
        # on créé un autre feed sur la base du premier pour élargir les horaires
        feed_temp = gtfs_feed(self._Feed.gtfs_path,
                              date=self._Feed.date,
                              plage_horaire=plage_horaire,
                              methode = self._Feed.methode)
        
        table = feed_temp.table_horaire()
        
        maxh = list(); minh = list()
        for route in table.route_short_name.unique():
            tmp = table[table['route_short_name'] == route]
            maxh.append(max(tmp.arrival_time))
            minh.append(min(tmp.departure_time))
            
        df = pd.DataFrame()
        df['route_short_name'] = table.route_short_name.unique()
        df['min'] = seconds_to_hms(minh)
        df['max'] = seconds_to_hms(maxh)
        df["amplitude (sec.)"] = np.array(maxh) - np.array(minh)
        
        return df
    
    
    def _get_trace_des_lignes(self):
        
        shapes = self._Feed.shapes
        trips = self._Feed.trips
        routes = self._Feed.routes
        
        if not shapes.empty:
            list_lines = list()
            for id_ in shapes.shape_id.unique():
                tmp = shapes[shapes.shape_id == id_]
                list_points = list()
                for lat, lon in zip(tmp.shape_pt_lat, tmp.shape_pt_lon):
                    list_points.append(Point([lon, lat]))
                list_lines.append(LineString(list_points))
            gs = gpd.GeoSeries(list_lines)
            
            geo = gpd.GeoDataFrame(shapes.shape_id.unique(),
                                   geometry = gs)#.set_crs('epsg:4326'))
            
            geo.rename(columns = {
                0 : 'shape_id'}, inplace = True)
            
            # on créé un fichier de fusion trips/routes pour associer le trip_id
            # à la route_short_name :
            tmp = trips[['trip_id', 'route_id', "shape_id"]].merge(routes[['route_id', 'route_short_name']],
                                                       on = "route_id")
            
            # conversion des trip_ids en strings:
            geo.shape_id = geo.shape_id.astype(str)
            tmp.shape_id = tmp.shape_id.astype(str)
            
            # fusion :
            geo = geo.merge(tmp, on = "shape_id")
            
            
            return geo
        else:
            print('pas de fichier shape')
            return gpd.GeoDataFrame()

