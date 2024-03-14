from expreseau_gtfs.analyses import gtfs_feed
from expreseau_gtfs.sections import sections


fic = "gtfs.zip"

gf = gtfs_feed(fic)

freq_segments = gf.frequence_par_segment(date_demandee = "20240201",
                                    plage_horaire = [7, 8], coords=True)

segments = freq_segments[freq_segments.route_short_name == "A"]

gs = sections(df=segments)
stops = gf.stops
stops.stop_id = stops.stop_id.astype(str)
gda = gs.decoupe_auto()