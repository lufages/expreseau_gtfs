import pandas as pd
import zipfile
from datetime import datetime
import datetime as dtm
import os
import numpy as np
import expreseau_gtfs
from shapely import Point, LineString
import geopandas as gpd
import seaborn as sb
import matplotlib.pyplot as plt

class gtfs_feed:    
    
    def __init__(self,
                 gtfs_path : str):
        
        self._gtfs_path = gtfs_path
        self._trips = None
        self._routes = None
        self._shapes = None
        self._stops = None
        self._stop_times = None
        self._calendar = None
        self._calendar_dates= None
        self._frequence_par_ligne = None

   # setters     
    @property
    def gtfs_path(self):
        return self._gtfs_path
    @property
    def trips(self):
        return self._get_trips()
    @property
    def routes(self):
        return self._get_routes()
    @property
    def shapes(self):
        return self._get_shapes()
    @property
    def stops(self):
        return self._get_stops()
    @property
    def stop_times(self):
        return self._get_stop_times()
    @property
    def calendar(self):
        return self._get_calendar()
    @property
    def calendar_dates(self):
        return self._get_calendar_dates()
    
    
    
    #getters fichiers gtfs
    def _get_trips(self):
        return reader("trips", self._gtfs_path)
    def _get_routes(self):
        return reader("routes", self._gtfs_path)
    def _get_shapes(self):
        return reader("shapes", self._gtfs_path)
    def _get_stops(self):
        return reader("stops", self._gtfs_path)
    def _get_stop_times(self):
        return reader("stop_times", self._gtfs_path)
    def _get_calendar(self):
        return reader("calendar", self._gtfs_path)
    def _get_calendar_dates(self):
        return reader("calendar_dates", self._gtfs_path)
    
    
    def frequence_par_ligne(self, date_demandee = "20240123",
                            plage_horaire = [8,9],
                            stop_sequence = 1):
        """
        Parameters
        ----------
        date_demandee : TYPE, optional
            DESCRIPTION. The default is "20240123".
        plage_horaire : TYPE, optional
            DESCRIPTION. The default is [8,9].

        Returns : pandas dataframe avec la fréquence par ligne et le temps 
        d'attente moyen.
        -------
        TYPE
            DESCRIPTION.

        """
        
        return self._get_frequence_par_ligne(date_demandee,plage_horaire,
                                             stop_sequence)
    
    def table_horaire_jour_demande(self, date_demandee, plage_horaire):
        """
        Parameters
        ----------
        date_demandee : date au format "YYYYMMDD".
        plage_horaire : liste d'entier à raisonner comme intervalles ouverts.

        Returns : pandas dataframe avec les stops et leurs passages, lignes, etc
        -------
        TYPE
            DESCRIPTION.

        """
        return self._get_table_horaire_jour_demande(date_demandee,plage_horaire)
    
    def amplitude_par_ligne(self, date_demandee):
        return self._get_amplitude_par_ligne(date_demandee)
    
    def services_exceptes(self, date_demandee):
        """
        Renvoit la liste des services concernés par une exception le jour
        demandé.
        Parameters
        ----------
        date_demandee : "YYYYMMDD"

        Returns : list()
        -------
        """
        return self._get_services_exceptions(date_demandee)
    
    def services(self, date_demandee):
        """
        renvoit la liste des services circulant le jour demandé

        Parameters
        ----------
        date_demandee : "YYYYMMDD"

        Returns : list()
        -------

        """
        return self._get_services(date_demandee)
    
    def frequence_par_segment(self, date_demandee, plage_horaire, coords = False):
        """
        Parameters
        ----------
        date_demandee : "YYYYMMDD"
        plage_horaire : [8, 9]

        Returns : pandas dataframe des fréquences par segment et par ligne
        -------
        """
        return self._get_frequence_par_segment(date_demandee, plage_horaire, coords)
    
    def traces_des_lignes(self, date_demandee, plage_horaire):
        """
        Parameters
        ----------
        date_demandee : TYPE
            DESCRIPTION.
        plage_horaire : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        return self._get_trace_des_lignes(date_demandee, plage_horaire)
    # getters
    
    def frequence_par_shapes(self, date_demandee = "20240123",
                            plage_horaire = [8,9],
                            stop_sequence = 1):
        """

        Parameters
        ----------
        date_demandee : str "YYYYMMDD", optional
            DESCRIPTION. The default is "20240123".
        plage_horaire : list() : [7, 9], optional
            DESCRIPTION. The default is [8,9].
        stop_sequence : int, optional
            DESCRIPTION. The default is 1.

        Returns pandas DataFrame()
        -------

        """
        return self._get_frequence_par_shape(date_demandee, plage_horaire, stop_sequence)

    
    def evol_journaliere(self, date_demandee):
        return self._get_evol_journaliere(date_demandee)
    
    def evol_journaliere_ligne(self, date_demandee, ligne):
        return self._get_evol_journaliere_ligne(date_demandee, ligne)
    
    def plot_evol_journaliere(self, date_demandee, titre = None,
                              x_axe = None, y_axe = None,
                              liste_ligne_a_tracer = None):
        evol = self._get_evol_journaliere(date_demandee)
        evol['twindow'] = evol['twindow'].astype(str)
        fig, ax1 = plt.subplots()
        sb.lineplot(data=evol,
              x='twindow',
              y="trip_id",linestyle="dashed",color="black", label = 'Ensemble')
        if liste_ligne_a_tracer != None:
            ax2 = ax1.twinx()
            for ligne in liste_ligne_a_tracer:
                ev_ligne = self.evol_journaliere_ligne(date_demandee, ligne)
                ev_ligne['twindow'] = ev_ligne['twindow'].astype(str)
                ev_ligne = ev_ligne.merge(evol[['twindow']], on = "twindow")
                sb.lineplot(data=ev_ligne,
                      x='twindow',
                      y="trip_id",marker="o", label = ligne)
        
        ax1.set_title(titre)
        ax1.set_xlabel(x_axe)
        ax1.set_ylabel(y_axe)
        ax1.set_xticklabels(labels = evol['twindow'].values, rotation=90)
        
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        
        plt.grid()
        plt.show()
        
    def freq_min(self, date_demandee, plage_horaire = [7,21], stop_sequence = 8):
        return self._get_freq_min(date_demandee, stop_sequence, plage_horaire)

########## getters  


    def _get_freq_min(self, date_demandee,
                      stop_sequence, 
                      plage_horaire):
        
        # il faut calculer la fréquence par heure de 7h à 21h par ligne
        # recupère la table horaire avec les services circulant le jour demandé entre 7h et 21h (par défaut)
        trips_stops = self.table_horaire_jour_demande(date_demandee, plage_horaire)
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
        coef = plage_horaire[1] - plage_horaire[0]
        trips_stops_["freq"] = coef * 60 / trips_stops_['count']
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

    def _get_evol_journaliere(self, date_demandee):
        
        table = self._get_table_horaire_jour_demande(date_demandee,
                                        [0,25])#.drop(columns='pickup_type')
        
        table['arrival_time'] = table.arrival_time.values / 3600
        
        table['twindow'] = pd.cut(x=table['arrival_time'], bins=np.arange(5,25))
        serv_excep = self.services_exceptes(date_demandee)
        table = table[~table.service_id.isin(serv_excep)]
        table = table[table.stop_sequence == 5]
        evol_totale = table[['twindow', 'trip_id']]\
                    .groupby('twindow').count().reset_index()
                    
        return evol_totale
    
    def _get_evol_journaliere_ligne(self, date_demandee, ligne):
        
        table = self._get_table_horaire_jour_demande(date_demandee,
                                        [0,25])#.drop(columns='pickup_type')
        
        table['arrival_time'] = table.arrival_time.values / 3600
        
        table['twindow'] = pd.cut(x=table['arrival_time'], bins=np.arange(5,25))
        serv_excep = self.services_exceptes(date_demandee)
        table = table[~table.service_id.isin(serv_excep)]
        table = table[table.route_short_name == ligne]
        table = table[table.stop_sequence == 1]
        evol_totale = table[['twindow', 'trip_id']]\
                    .groupby('twindow').count().reset_index()
                    
        return evol_totale

 
    def _get_frequence_par_segment(self, date_demandee, plage_horaire, coords):
    
        stops = self.stops
        # extraction de la table horaire :
        table = self.table_horaire_jour_demande(date_demandee, plage_horaire)
        # on retire les services sous exception :
        liste_service_except = self.services_exceptes(date_demandee)
        table = table[~table.service_id.isin(liste_service_except)]
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
        # Au passage on enregistre ces résultats dans un df apelé fréquence :
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

        return segments_freq
    
    def _get_frequence_par_ligne(self, date_demandee,plage_horaire, stop_sequence):
        # trips = self.trips
        routes = self.routes
        calendar_dates = self.calendar_dates
        
        # on appelle la tbale horaire :
        trips_stops = self.table_horaire_jour_demande(date_demandee, plage_horaire)
        trips_stops = trips_stops[['route_id','route_short_name', 'trip_id',
                    'direction_id', 'service_id', "stop_sequence", 'stop_id']]
        
        # st on retire les anomalies (fonctionne dans le cas de Nice) :
        # freq_trips = freq_trips[freq_trips.apply(lambda row: row['trip_id'].\
            # find(row['service_id']) != -1, axis=1)]
        
        # soit on retire les exceptions pour le jour spécifié :
        liste_service_except = calendar_dates[calendar_dates['date']\
                                .isin([int(date_demandee)])].service_id.to_list()
            # les exceptions sont dans le fichier calendar_dates
        # on retire la liste des services exceptionnels :
        trips_stops =  trips_stops[~trips_stops.service_id.isin(liste_service_except)]
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
        
        # affichage
        return freq_trips#.sort_values(by='nbtrips', ascending=False).head(15)
        
    def _get_frequence_par_shape(self, date_demandee,plage_horaire, stop_sequence):
        # trips = self.trips
        routes = self.routes
        calendar_dates = self.calendar_dates
        
        # on appelle la tbale horaire :
        trips_stops = self.table_horaire_jour_demande(date_demandee, plage_horaire)
        trips_stops = trips_stops[['shape_id','route_id', 'route_short_name', 'trip_id',
                    'direction_id', 'service_id', "stop_sequence", 'stop_id']]
        
        # st on retire les anomalies (fonctionne dans le cas de Nice) :
        # freq_trips = freq_trips[freq_trips.apply(lambda row: row['trip_id'].\
            # find(row['service_id']) != -1, axis=1)]
        
        # soit on retire les exceptions pour le jour spécifié :
        liste_service_except = calendar_dates[calendar_dates['date']\
                                .isin([int(date_demandee)])].service_id.to_list()
            # les exceptions sont dans le fichier calendar_dates
        # on retire la liste des services exceptionnels :
        trips_stops =  trips_stops[~trips_stops.service_id.isin(liste_service_except)]
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
        
        # affichage
        return freq_trips_shapes
    
    def _get_services(self, date_demandee):
        
        calendar = self.calendar
        
        calendar['start_date'] = pd.to_datetime(calendar['start_date'], format="%Y%m%d")
        calendar['end_date'] = pd.to_datetime(calendar['end_date'], format="%Y%m%d")
        # on tri les tables selon la date renseignee
        date = datetime.strptime(date_demandee,"%Y%m%d") # conversion en datetime
        # Obtenir le nom du jour de la semaine
        nom_jour = date.strftime('%A').lower()
        # Trouver l'intervalle de dates dans lequel est la date cherchée :
        resultat = trouver_intervalle(date_demandee, calendar)
        
        # calucler la liste de services triés par la date et le jour (lundi, mardi, etc ) demandé :
        liste_services = resultat[['service_id', nom_jour]]\
            [resultat[['service_id', nom_jour]][nom_jour]==1].service_id
        # print(liste_services)
        if liste_services.empty:
            print("pas de service")
        return liste_services
    
    
    def _get_services_exceptions(self, date_demandee):
        
        calendar_dates = self.calendar_dates        
        liste_service_exceptes = calendar_dates[calendar_dates['date']\
                                .isin([int(date_demandee)])].service_id.to_list()
        
        return liste_service_exceptes
    
    
    def _get_amplitude_par_ligne(self, date_demandee):
        
        table = self.table_horaire_jour_demande(date_demandee,
                                                [0,25])
        maxh = list(); minh = list()
        for route in table.route_id.unique():
            tmp = table[table['route_id'] == route]
            maxh.append(max(tmp.arrival_time))
            minh.append(min(tmp.departure_time))
            
        df = pd.DataFrame()
        df['route_short_name'] = table.route_short_name.unique()
        df['min'] = seconds_to_hms(minh)
        df['max'] = seconds_to_hms(maxh)
        
        return df
    
    
    def _get_table_horaire_jour_demande(self, date_demandee, plage_horaire):
        trips = self.trips
        routes = self.routes
        calendar = self.calendar
        stop_times = self.stop_times
        # calendar_dates = self.calendar_dates
        
        # on merge les tables routes et trips :
        if 'shape_id' in routes:
            trips_routes = trips.merge(routes, on = "route_id")\
                [['route_id','route_short_name',  'trip_id',
                  'direction_id', "service_id",'shape_id']]##, "trip_headsign" ]]
        else:
            trips_routes = trips.merge(routes, on = "route_id")\
                [['route_id','route_short_name',  'trip_id',
                  'direction_id', "service_id"]]            
            
       # on convertit les dates en datetime :
        calendar['start_date'] = pd.to_datetime(calendar['start_date'], format="%Y%m%d")
        calendar['end_date'] = pd.to_datetime(calendar['end_date'], format="%Y%m%d")
    
        # on tri les tables selon la date renseignee
        date = datetime.strptime(date_demandee,"%Y%m%d") # conversion en datetime
        # Obtenir le nom du jour de la semaine
        nom_jour = date.strftime('%A').lower()
        # Trouver l'intervalle de dates dans lequel est la date cherchée :
        resultat = trouver_intervalle(date_demandee, calendar)
        
        # calucler la liste de services triés par la date et le jour (lundi, mardi, etc ) demandé :
        liste_services = resultat[['service_id', nom_jour]]\
            [resultat[['service_id', nom_jour]][nom_jour]==1].service_id
        # print(liste_services)
        if liste_services.empty:
            print("pas de service")
        
        # on fusion avec la table trips_route :
        trips_routes_services = trips_routes.merge(liste_services, on = "service_id")
        # on créé une table horaire des trips passant à chaque arrêt et on convertit les horaires en secondes 
        table_hr = stop_times.copy()
        table_hr['arrival_time'] = pd.to_timedelta(table_hr['arrival_time']).dt.total_seconds()
        table_hr['departure_time'] = pd.to_timedelta(table_hr['departure_time']).dt.total_seconds()
        # on tri les horaires selon une plage
        # on stocke ça dans un nouveau dataframe :
        table_hr_fr = table_hr[(table_hr.arrival_time <= plage_horaire[1]*3600) &
                               (table_hr.departure_time >= plage_horaire[0]*3600)]
        # on fusionne la table horaire avec les trips routes services :
        trips_stops = trips_routes_services.merge(table_hr_fr, on = "trip_id")
        # trips_stops = trips_stops[['route_id','route_short_name', 'trip_id',
        #             'direction_id', 'service_id', "stop_sequence", 'stop_id']]
        
        return trips_stops
  
    
    def _get_trace_des_lignes(self, date_demandee, plage_horaire):
        shapes = self.shapes
        # routes = self.routes
        # trips = self.trip
        # list_id = list()
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
        
        return geo
    
def reader(file, gtfs_path):

    """
    Charge tous les fichiers d'un fichier ZIP GTFS et les stocke dans
    un dictionnaire de DataFrames.
    Parameters:
    - zip_path (str): Chemin vers le fichier ZIP GTFS.    
    Returns:
    - dict: Un dictionnaire où les clés sont les noms de fichiers GTFS
    et les valeurs sont les DataFrames correspondants.
    """

    with zipfile.ZipFile(gtfs_path, 'r') as zip_file:
        # Liste tous les fichiers dans le ZIP
        zip_file_contents = zip_file.namelist()
        # Charge chaque fichier dans un DataFrame
        for file_name in zip_file_contents:
#             print(file_name)
            # Extrait le nom du fichier sans l'extension
            base_name, _ = os.path.splitext(os.path.basename(file_name))
            if base_name==file:
            # Charge le fichier dans un DataFrame
                with zip_file.open(file_name) as file:
                    df = pd.read_csv(file)
    return df


    # Fonction pour trouver l'intervalle contenant une date donnée
def trouver_intervalle(date_demandee, df):
    date_demandee = datetime.strptime(date_demandee, "%Y%m%d")
    masque = df.apply(lambda row: row['start_date'] <= date_demandee <= row['end_date'], axis=1)
    intervalle = df[masque]
    return intervalle

def seconds_to_hms(seconds):
    """
    convertit une liste de temps en secondes en format "hh:mm:ss"
    argument : liste de nombres réels
    sortie : chaîne de caractères
    """
    temps_formatte = list() # on instacie une liste vide dans laquelle on stockera les chaine des caractères
    for sec in seconds: # boucle sur toutes les entités de la liste de nombre réels
        delta = dtm.timedelta(seconds=sec) # on calcule le delta entre 00:00 et le 
                                                # nombre de secondes de l'entité courante
        # on converti en heures, minutes, secondes : 
        heures, remainder = divmod(delta.seconds, 3600)
        minutes, secondes = divmod(remainder, 60)
        # on convertit en string et on amende la liste
        temps_formatte.append('{:02}:{:02}:{:02}'.format(heures, minutes, secondes))
    # on renvoit la liste de strings
    return temps_formatte