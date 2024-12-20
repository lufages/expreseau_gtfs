import zipfile
import os
import pandas as pd
from datetime import datetime
from expreseau_gtfs.utils import trouver_intervalle
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt
# from expreseau_gtfs.feed import gtfs_feed

class gtfs_feed(object):
    
    def __init__(self,
                 gtfs_path : str,
                 date : str,
                 plage_horaire : list(),
                 methode = "date") :
        
        self._gtfs_path = gtfs_path
        self._date = date
        self._plage_horaire = plage_horaire
        self._methode = methode
        
        self._trips = pd.DataFrame()
        self._routes = pd.DataFrame()
        self._shapes = pd.DataFrame()
        self._stops = pd.DataFrame()
        self._stop_times = pd.DataFrame()


# =============================================================================
#  Getters  /  setters     
# =============================================================================
    @property
    def gtfs_path(self):
        return self._gtfs_path
    @property
    def date(self):
        return self._date    
    @property
    def plage_horaire(self):
        return self._plage_horaire
    @property
    def methode(self):
        return self._methode
    
    @property
    def trips(self):
        self._trips = self._get_trips()
        return self._trips
    
    @trips.setter
    def trips(self, value):
        self._trips = value

    
    
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
    

        
    @stop_times.setter
    def stop_times(self, values):
        self._stop_times = values
        
    @shapes.setter
    def shapes(self, values):

        self._shapes = values
    
    
    #getters fichiers gtfs
    # données impactées par les services :
    def _get_trips(self):
        trips = self._trips
        if self._trips.empty:
            trips = self._get_data("trips")
            
            if self._methode == "date":
                services = self._get_services()
                trips = trips[trips.service_id.isin(services.service_id)]
            elif self._methode == "service":
                # on récupère le num de service qui a le nb de service le plus important : (le premier):
                max_services = trips[['service_id']].value_counts().index[0][0]
                trips = trips[trips.service_id == max_services]
            else:
                print("Methode argument must take values among 'date' and 'service'")
                return 0
        return trips
    
    def _get_shapes(self):
        
        shapes = self._shapes
        if self._shapes.empty:
            shapes = self._get_data("shapes")
            # on charge les trips circulant le jour et l'heure souhaités:
            shape_id = self._get_trips()["shape_id"].values
            shapes = shapes[shapes.shape_id.isin(shape_id)]
        return shapes
    
    def _get_stop_times(self):
        stop_times = self._stop_times
        if self._stop_times.empty:
            stop_times = self._get_data("stop_times")
            # on charge les trips circulant le jour et l'heure souhaités:
            trip_id = self._get_trips()["trip_id"].values
            stop_times = stop_times[stop_times.trip_id.isin(trip_id)]
        return stop_times
    
    # données non impactées par les services :
    def _get_stops(self):
        return self._get_data("stops")
    def _get_routes(self):
        return self._get_data("routes")
    def _get_calendar(self):
        return self._get_data("calendar")
    def _get_calendar_dates(self):
        return self._get_data("calendar_dates")
    
# =============================================================================
# Code 
# =============================================================================
    
 
    def data(self, name_fic):
        """        
        Renvoit le fichier brut spécifié (trips, routes, etc.)
        
        Parameters
        ----------
        name_fic : 
            Nom du fichier texte sans l'extension : p.ex. : "trips"

        Returns
        -------
        pandas.dataframe()
            Renvoit le fichier sous forme de dataframe.

        """

        return self._get_data(name_fic)
 
    def services_exceptes(self):
        """
        Renvoit la liste des services concernés par une exception le jour
        demandé.

        Returns
        -------
        python list()

        """

        return self._get_services_exceptions()
    
    def services(self):
        """
        Renvoit la liste des services circulant le jour demandé

        Returns
        -------
        python list()

        """
        return self._get_services()    
 
    
    def table_horaire(self):
        """
        Renvoit la table horaire (tous les arrêts et leurs passages par ligne et direction)

        Returns
        -------
        pandas.dataframe()
            Dataframe avec les stops et leurs horaires de passages, les lignes, les coordonnées, etc.

        """
        return self._get_table_horaire()
    
    
    def evol_journaliere(self, stop_sequence = 5):
        """
        Renvoit un pandas dataframe avec l'évolution par tranche horaire de 1h 
        pour l'ensemble des lignes du réseau.
        
        Parameters
        ----------
        stop_sequence : int, optional
            Séquence de l'arrêt sur la ligne (1er, 2ème, etc.). La valeur par défaut est 5.

        Returns
        -------
        pandas.dataframe()
            
        """

        return self._get_evol_journaliere(stop_sequence)
    
    def evol_journaliere_ligne(self, ligne, stop_sequence = 5):
        """
        Renvoit un pandas dataframe avec l'évolution par tranche horaire de 1h 
        pour la ou les lignes spécifiées.

        Parameters
        ----------
        ligne : list()
            Liste de lignes dont on veut connaitre l'évolution de la fréquentation.
            Pour spécifier une ligne, écrire sous la forme : ['ligne'].
        stop_sequence : int, optional
            Séquence de l'arrêt sur la ligne (1er, 2ème, etc.). La valeur par défaut est 5.

        Returns 
        -------
        pandas.dataframe()
            Le dataframe de l'évolution de la fréquence par heure.

        """

        return self._get_evol_journaliere_ligne(ligne, stop_sequence)
    
    
    def plot_evol_journaliere(self, titre = "Evolution journalière",
                              x_axe = None, y_axe_1 = "évol. ens. des lignes [nombre]",
                              liste_ligne_a_tracer = None,
                              y_axe_2="évol. lignes spécif. [nombre]"):
        """
        Plot matplotlib de l'évolution de l'offre par heure. Possibilité d'analyser
        cette évolution pour certaines lignes en les ajoutant sous forme de liste.

        Parameters
        ----------
        titre : str, optionnal
            Par défaut : "Evolution journalière".
        x_axe : str, optionnal
        y_axe_1 : str, optionnal
            Titre de l'axe y de gauche (ensemble des lignes). Par défaut : "évol. ens. des lignes [nombre]".
        liste_ligne_a_tracer : list(), optionnal
            Liste des lignes à ajouter au graphique.
        y_axe_2 : str, optionnal
            Titre de l'axe y de droite (lignes spécifiées).
            Par défaut : "évol. lignes spécif. [nombre]".

        """
        evol = self._get_evol_journaliere(stop_sequence=5)
        evol['twindow'] = evol['twindow'].astype(str)
        fig, ax1 = plt.subplots()
        sb.lineplot(data=evol,
              x='twindow',
              y="trip_id",linestyle="dashed",color="black", label = 'Ensemble')
        if liste_ligne_a_tracer != None:
            ax2 = ax1.twinx()
            for ligne in liste_ligne_a_tracer:
                ev_ligne = self.evol_journaliere_ligne(ligne, stop_sequence=5)
                ev_ligne['twindow'] = ev_ligne['twindow'].astype(str)
                ev_ligne = ev_ligne.merge(evol[['twindow']], on = "twindow")
                sb.lineplot(data=ev_ligne,
                      x='twindow',
                      y="trip_id",marker="o", label = ligne)
                ax2.set_ylabel(y_axe_2)
                ax2.legend(loc='upper right')

        
        ax1.set_title(titre)
        ax1.set_xlabel(x_axe)
        ax1.set_ylabel(y_axe_1)
        ax1.set_xticklabels(labels = evol['twindow'].values, rotation=90)
        
        ax1.legend(loc='upper left')
        
        plt.grid()
        plt.show()    
 
    
 
    def _get_data(self, name_fic):
        return self._reader(name_fic, self._gtfs_path)
    
   
    def _get_table_horaire(self):
        
        date_demandee = self.date
        plage_horaire = self._plage_horaire
        
        trips = self._get_trips()
        routes = self._get_routes()
        calendar = self._get_calendar()
        stop_times = self._get_stop_times()
        
        # on merge les tables routes et trips :
        if 'shape_id' in trips:
            trips_routes = trips.merge(routes, on = "route_id")\
                [['route_id','route_short_name',  'trip_id',
                  'direction_id', "service_id",'shape_id']]##, "trip_headsign" ]]
        else:
            trips_routes = trips.merge(routes, on = "route_id")\
                [['route_id','route_short_name',  'trip_id',
                  'direction_id', "service_id"]]     
                
        if self._methode == "date":
            
            if not calendar.empty:    
               # on convertit les dates en datetime :
                calendar['start_date'] = pd.to_datetime(calendar['start_date'], format="%Y%m%d")
                calendar['end_date'] = pd.to_datetime(calendar['end_date'], format="%Y%m%d")
            
                # on tri les tables selon la date renseignee
                date = datetime.strptime(date_demandee,"%Y%m%d") # conversion en datetime
                # Obtenir le nom du jour de la semaine
                nom_jour = date.strftime('%A').lower()
                # Trouver l'intervalle de dates dans lequel est la date cherchée :
                resultat = trouver_intervalle(date_demandee, calendar)
                
                # calculer la liste de services triés par la date et le jour (lundi, mardi, etc ) demandé :
                liste_services = resultat[['service_id', nom_jour]]\
                    [resultat[['service_id', nom_jour]][nom_jour]==1].service_id
                
                # on fusion avec la table trips_route :
                trips_routes_services = trips_routes.merge(liste_services, on = "service_id")
                
                # on retire les services exceptes:
                serv_exc = self._get_services_exceptions()
                trips_routes_services = trips_routes_services[~trips_routes_services.service_id.isin(serv_exc)]
                
                # print(liste_services)
                if liste_services.empty:
                    print("pas de service")
            
            else: # on utilise le fichier calendar_dates:
                calendar = self._get_calendar_dates()
                calendar['date'] = calendar['date'].astype(str)
                liste_services = calendar[calendar.date == date_demandee].service_id
                trips_routes_services = trips_routes.merge(liste_services, on = "service_id")
                
        elif self._methode == "service":
            
            liste_services = trips[['service_id']].value_counts()
            # on fusion avec la table trips_route :
            trips_routes_services = trips_routes.merge(liste_services, on = "service_id")
                
        else:
            print("'Methode' argument must take values among 'date' and 'service'")
            return 0
        
        

            
    
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

        
        return trips_stops
    
    def _get_services(self):
        
        date_demandee = self._date
        calendar = self._get_calendar()
        if not calendar.empty:
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
                [resultat[['service_id', nom_jour]][nom_jour]==1]
            # print(liste_services)
        
        else:# on utilise le fichier calendar_dates:
            calendar = self._get_calendar_dates()
            calendar['date'] = calendar['date'].astype(str)
            liste_services = calendar[calendar.date == date_demandee]
        
        if liste_services.empty:
            print("pas de service")
        return liste_services
    
    
    def _get_services_exceptions(self):
        
        date_demandee = self._date
        calendar_dates = self._get_calendar_dates()      
        liste_service_exceptes = calendar_dates[calendar_dates['date']\
         .isin([int(date_demandee)]) & (calendar_dates.exception_type == 2)].service_id.to_list()
        
        return liste_service_exceptes
    
    
    def _get_evol_journaliere(self, stop_sequence):
        
        plage_horaire=[0, 25]
        
        # on créé un autre feed sur la base du premier pour élargir les horaires
        feed_temp = gtfs_feed(self._gtfs_path,
                              date=self._date,
                              plage_horaire=plage_horaire)
        
        table = feed_temp.table_horaire()
        
        table['arrival_time'] = table.arrival_time.values / 3600
        
        table['twindow'] = pd.cut(x=table['arrival_time'], bins=np.arange(5,25))

        table = table[table.stop_sequence == stop_sequence]
        evol_totale = table[['twindow', 'trip_id']]\
                    .groupby('twindow').count().reset_index()
                    
        return evol_totale
    
    def _get_evol_journaliere_ligne(self, ligne, stop_sequence):
        
        plage_horaire=[0, 25]
        
        # on créé un autre feed sur la base du premier pour élargir les horaires
        feed_temp = gtfs_feed(self._gtfs_path,
                              date=self._date,
                              plage_horaire=plage_horaire)
        
        
        table = feed_temp.table_horaire()
        
        table['arrival_time'] = table.arrival_time.values / 3600
        
        table['twindow'] = pd.cut(x=table['arrival_time'], bins=np.arange(5,25))

        table = table[table.route_short_name == ligne]
        table = table[table.stop_sequence == stop_sequence]
        evol_totale = table[['twindow', 'trip_id']]\
                    .groupby('twindow').count().reset_index()
                    
        return evol_totale
    
    
    def _reader(self, file, gtfs_path):

        df = pd.DataFrame([])
        with zipfile.ZipFile(gtfs_path, 'r') as zip_file:
            # Liste tous les fichiers dans le ZIP
            zip_file_contents = zip_file.namelist()
            # Charge chaque fichier dans un DataFrame
            for file_name in zip_file_contents:
                # Extrait le nom du fichier sans l'extension
                base_name, _ = os.path.splitext(os.path.basename(file_name))
                if base_name==file:
                # Charge le fichier dans un DataFrame
                    with zip_file.open(file_name) as file:
                        df = pd.read_csv(file)

        return df

