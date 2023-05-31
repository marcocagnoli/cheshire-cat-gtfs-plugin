from cat.mad_hatter.decorators import tool, hook
import requests
import json
from datetime import datetime, timezone
from dateutil import tz
from os.path import exists

@tool(return_direct=True)
def bus_stop_eta (stop_code: str, cat):
    """Use to retrieve which bus is arriving to a bus stop. Input is the bus stop code."""
    
    conf = CheckConfiguration()
    
    if conf == None or conf["apikey"] == None:
        answer = """
    In order to give you these information, I need three configuration parameters. I need to save Api Key.

    Which is Tranit Land Api Key?
    """
        return answer
    elif conf["onestopid"] == None:
        return "I need to save Transit Land OneStopID. Which is Transit Land OneStopID?"
    elif conf["timezone"] == None:
        return "I need to save GTFS TimeZone. Which is GTFS TimeZone?"

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
        
        answer = "These are next arrivals at bus stop\n"
        answer += "&nbsp;\n"
        answer += "**" + stop_name + "** (" + stop_code + "):\n"
        answer += "&nbsp;\n"
        answer += "| &nbsp; Route &nbsp; | &nbsp; &nbsp; &nbsp; Company &nbsp; &nbsp; &nbsp; | &nbsp; &nbsp; &nbsp; Destination &nbsp; &nbsp; &nbsp; | &nbsp; &nbsp; &nbsp; Minutes &nbsp; &nbsp; &nbsp; | &nbsp; &nbsp; &nbsp; Real Time &nbsp; &nbsp; &nbsp; |\n"
        answer += "|:----------:|:----------:|:----------:|:----------:|:----------:|\n"
    
        routes = []
        
        for departure in stop['departures']:
    
            realtime = False
            
            if departure['arrival']['estimated'] is not None:
                realtime = True
            
            if realtime == True:
                
                if departure['trip']['route']['route_short_name'] not in routes:
                    routes.append(departure['trip']['route']['route_short_name'])
                
                minutes = round((datetime.strptime(departure['service_date'] + " " + departure['arrival']['estimated'], "%Y-%m-%d %H:%M:%S") - convertUTCToGTFSTime(datetime.utcnow(), gtfstimezone)).total_seconds() / 60)
                
                if minutes < 0:
                    minutes = 0
                        
                answer += "|" + departure['trip']['route']['route_short_name'] + "|" + departure['trip']['route']['agency']['agency_name'] + "|"+ departure['trip']['trip_headsign'] + "|" + str(minutes) + "|YES|\n"
                
        l = len(routes)
        
        for departure in stop['departures']:

            realtime = False
            
            if departure['arrival']['estimated'] is not None:
                realtime = True
            
            if realtime == False:
                
                if departure['trip']['route']['route_short_name'] not in routes:
                    routes.append(departure['trip']['route']['route_short_name'])
                
                    minutes = round((datetime.strptime(departure['service_date'] + " " + departure['arrival']['scheduled'], "%Y-%m-%d %H:%M:%S") - convertUTCToGTFSTime(datetime.utcnow(), gtfstimezone)).total_seconds() / 60)
                    
                    if minutes < 0:
                        minutes = 0
                        
                    answer += "|" + departure['trip']['route']['route_short_name'] + "|" + departure['trip']['route']['agency']['agency_name'] + "|"+ departure['trip']['trip_headsign'] + "|" + str(minutes) + "|NO|\n"

    return (answer)

@tool(return_direct=True)
def save_apikey (apikey: str, cat):
    """Use this tool to save Transit Land Api Key. Input is the Api Key."""
    
    data = ""
    
    if not exists('./cat/plugins/gtfs/gtfs-config.json'):
        
        data = {
            'apikey' : apikey,
            'onestopid' : None,
            'timezone' : None
        }
    
    else:
        
        with open('./cat/plugins/gtfs/gtfs-config.json') as json_file:
            data = json.load(json_file)
        
            data["apikey"] = apikey
            
    with open('./cat/plugins/gtfs/gtfs-config.json', 'w') as outfile:
        json.dump(data, outfile)
    
    conf = CheckConfiguration()
    
    if conf == None or conf["apikey"] == None:
        return "I need to save Api Key. Which is Tranit Land Api Key?"
    elif conf["onestopid"] == None:
        return "I need to save Transit Land OneStopID. Which is Transit Land OneStopID?"
    elif conf["timezone"] == None:
        return "I need to save GTFS TimeZone. Which is GTFS TimeZone?"
    else:       
        return "Ok, I've saved the api key. At what bus stop are you waiting?"

@tool(return_direct=True)
def save_onestopid (onestopid: str, cat):
    """Use this tool to save Transit Land OneStopID. Input is the OneStopID."""

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
        
    conf = CheckConfiguration()
    
    if conf == None or conf["apikey"] == None:
        return "I need to save Api Key. Which is Tranit Land Api Key?"
    elif conf["onestopid"] == None:
        return "I need to save Transit Land OneStopID. Which is Transit Land OneStopID?"
    elif conf["timezone"] == None:
        return "I need to save GTFS TimeZone. Which is GTFS TimeZone?"
    else:       
        return "Ok, I've saved the api key. At what bus stop are you waiting?"

@tool(return_direct=True)
def save_timezone (timezone: str, cat):
    """Use this tool to save GTFS TimeZone. Input is the GTFS TimeZone."""

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
    
    if not exists('./cat/plugins/gtfs/gtfs-config.json'):
        return None
    else:
        with open('./cat/plugins/gtfs/gtfs-config.json') as json_file:
            return json.load(json_file)
            