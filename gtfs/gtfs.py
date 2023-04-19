from cat.mad_hatter.decorators import tool, hook
import requests
import json
from datetime import datetime, timezone
from dateutil import tz

@tool(return_direct=True)
def bus_stop_eta (stop_code: str, cat):
    """Use to retrieve what bus is arriving at a stop. Input is the code (or the number) of the bus stop and should be wrapped into double quotes."""

    # ----- start configuration ---------
    
    # get a free api key from https://www.transit.land/
    
    transitland_apikey = "<apikey>"

    # in the same websie, find your feed onestopid. For example, for Rome, it is "f-sr-atac~romatpl~trenitalia"
    
    onestopid = "<onestopid>"
    
    # This is the GTFS timezone i.e. "Europe/Rome"
    
    gtfstimezone = "<timezone>"
    
    # ----- end  configuration ---------
    
    url = "https://transit.land/api/v2/rest/stops/" + onestopid + ":" + stop_code + "/departures"
    headers = {"apikey": transitland_apikey}
    
    response = requests.get(url, headers=headers)
    
    eta = response.json()

    for stop in eta['stops']:
        
        stop_name = stop["stop_name"]
        
        answer = "These are next arrivals at bus stop \"" + stop_name + "\" (" + stop_code + "):\n\n"
    
        routes = []
        
        for departure in stop['departures']:
    
            realtime = False
            
            if departure['arrival']['estimated'] is not None:
                realtime = True
            
            if realtime == True:
                
                if departure['trip']['route']['route_short_name'] not in routes:
                    routes.append(departure['trip']['route']['route_short_name'])
                
                if len(routes) == 1:
                    answer += "REAL TIME DATA" + "\n\n"
                
                answer += "Route: " + departure['trip']['route']['route_short_name'] + "\n"
                answer += "Company: " + departure['trip']['route']['agency']['agency_name'] +"\n"
                answer += "Destination: " + departure['trip']['trip_headsign'] + "\n"

                minutes = round((datetime.strptime(departure['service_date'] + " " + departure['arrival']['estimated'], "%Y-%m-%d %H:%M:%S") - convertUTCToGTFSTime(datetime.utcnow(), gtfstimezone)).total_seconds() / 60)
                
                if minutes < 0:
                    minutes = 0
                        
                answer += "Minutes: " + str(minutes) + "\n\n"
                
        l = len(routes)
        
        for departure in stop['departures']:

            realtime = False
            
            if departure['arrival']['estimated'] is not None:
                realtime = True
            
            if realtime == False:
                
                if departure['trip']['route']['route_short_name'] not in routes:
                    routes.append(departure['trip']['route']['route_short_name'])
                
                    if (len(routes) -l) == 1:
                        answer += "SCHEDULED DATA" + "\n\n"
                
                    answer += "Route: " + departure['trip']['route']['route_short_name'] + "\n"
                    answer += "Company: " + departure['trip']['route']['agency']['agency_name'] +"\n"
                    answer += "Destination: " + departure['trip']['trip_headsign'] + "\n"
                    
                    minutes = round((datetime.strptime(departure['service_date'] + " " + departure['arrival']['scheduled'], "%Y-%m-%d %H:%M:%S") - convertUTCToGTFSTime(datetime.utcnow(), gtfstimezone)).total_seconds() / 60)
                    
                    if minutes < 0:
                        minutes = 0
                        
                    answer += "Minutes (SCHEDULED): " + str(minutes) + "\n\n"

    return (answer)

def convertUTCToGTFSTime(utc, gtfstimezone):

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(gtfstimezone)

    utc = utc.replace(tzinfo=from_zone)

    return datetime.strptime(datetime.strftime(utc.astimezone(to_zone), "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
