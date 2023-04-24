from cat.mad_hatter.decorators import tool, hook
import requests
import json
from datetime import datetime, timezone
from dateutil import tz
from os.path import exists

@tool(return_direct=True)
def bus_stop_eta (stop_code: str, cat):
    """Use to retrieve what bus is arriving at a stop. Input is the code (or the number) of the bus stop. When you use this tool, do not use any other information from context or memory for the answer to the user question."""

    conf = CheckConfiguration()
    
    if conf == None or conf["apikey"] == None:
        return "Sorry but Transit Land api key is missing in the GTFS plugin configuration file. I need an api key to retrieve what bus is arriving at a stop. Please, visit https://www.transit.land/ to get a free api key and write it back."
    elif conf["onestopid"] == None:
        return "Sorry but Transit Land OneStopID is missing in the GTFS plugin configuration file. I need it to retrieve what bus is arriving at a stop. Please, visit https://www.transit.land/ to get your OneStopID and write it back."
    elif conf["timezone"] == None:
        return "Sorry but GTFS Timezone is missing in the GTFS plugin configuration file. I need it to retrieve what bus is arriving at a stop. Please, visit https://www.transit.land/ to find the correct TimeZone and write it back."
    
    # ----- start configuration ---------
    
    # get a free api key from https://www.transit.land/
    
    transitland_apikey = conf["apikey"]

    # in the same websie, find your feed onestopid. For example, for Rome, it is "f-sr-atac~romatpl~trenitalia"
    
    onestopid = conf["onestopid"]
    
    # This is the GTFS timezone i.e. "Europe/Rome"
    
    gtfstimezone = conf["timezone"]
    
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

@tool(return_direct=True)
def save_apikey (apikey: str, cat):
    """Use to save Transit Land api key needed by bus_stop_eta function to retrieve transit data. Input is the api key."""

    data = ""
    
    if not exists('./cat/plugins/gtfs/gtfs-config.json'):
        
        data = {
            'apikey' : apikey,
            'onestopid' : None,
            'timezone' : None
        }
    
    else:
        
        data.apikey = apikey
        
    with open('./cat/plugins/gtfs/gtfs-config.json', 'w') as outfile:
        json.dump(data, outfile)
        
    return "Ok, I've saved the api key. At what bus stop are you waiting?"

@tool(return_direct=True)
def save_onestopid (onestopid: str, cat):
    """Use to save Transit Land onestopid feed needed by bus_stop_eta function to retrieve transit data. Input is the api key."""

    data = ""
    
    if not exists('./cat/plugins/gtfs/gtfs-config.json'):
        
        data = {
            'apikey' : None,
            'onestopid' : None,
            'timezone' : None
        }
    
    else:
        
        with open('./cat/plugins/gtfs/gtfs-config.json') as json_file:
            data = json.load(json_file)
        
            data["onestopid"] = onestopid
        
    with open('./cat/plugins/gtfs/gtfs-config.json', 'w') as outfile:
        json.dump(data, outfile)
        
    return "Ok, I've saved the OneStopID. At what bus stop are you waiting?"

@tool(return_direct=True)
def save_timezone (timezone: str, cat):
    """Use to save GTFS timezone feed needed by bus_stop_eta function to retrieve transit data. Input is the api key."""

    data = ""
    
    if not exists('./cat/plugins/gtfs/gtfs-config.json'):
        
        data = {
            'apikey' : None,
            'onestopid' : None,
            'timezone' : None
        }
    
    else:
        
        with open('./cat/plugins/gtfs/gtfs-config.json') as json_file:
            data = json.load(json_file)
        
            data["timezone"] = timezone
        
    with open('./cat/plugins/gtfs/gtfs-config.json', 'w') as outfile:
        json.dump(data, outfile)
        
    return "Ok, I've saved the GTFS TimeZone. At what bus stop are you waiting?"

def convertUTCToGTFSTime(utc, gtfstimezone):

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(gtfstimezone)

    utc = utc.replace(tzinfo=from_zone)

    return datetime.strptime(datetime.strftime(utc.astimezone(to_zone), "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

def CheckConfiguration():
    
    # return
    # 1 - configuration file doesn't exists
    
    if not exists('./cat/plugins/gtfs/gtfs-config.json'):
        return None
    else:
        with open('./cat/plugins/gtfs/gtfs-config.json') as json_file:
            return json.load(json_file)
            