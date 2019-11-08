from math import radians, cos, sin, asin, sqrt
import pandas as pd
import os
import json
from typing import Set 
import requests

def get_closest_gage(gage_df:pd.DataFrame, station_df:pd.DataFrame, path_dir:str, start_row:int, end_row:int):
  # Function that calculates the closest weather stations to gage and stores in JSON
  for row in range(start_row, end_row):
    gage_info = {}
    gage_info["river_id"] = int(gage_df.iloc[row]['id'])
    gage_lat = gage_df.iloc[row]['latitude']
    gage_long = gage_df.iloc[row]['logitude']
    gage_info["stations"] = []
    total = len(station_df.index)
    for i in range(0, total):
      stat_row = station_df.iloc[i]
      dist = haversine(stat_row["lon"], stat_row["lat"], gage_long, gage_lat)
      st_id = stat_row['stid']
      gage_info["stations"].append({"station_id":st_id, "dist":dist})
    gage_info["stations"] = sorted(gage_info['stations'], key = lambda i: i["dist"], reverse=True) 
    with open(os.path.join(path_dir, str(gage_info["river_id"]) + "stations.json"), 'w') as w:
      json.dump(gage_info, w)
      if count%100 == 0:
        print("Currently at " + str(count))
      count +=1 
      
def get_weather_data(file_path:str, econet_gages:Set, base_url:str):
  """
  Function that retrieves if station has weather 
  data for a specific gage either from ASOS or ECONet 
  """
  gage_meta_info = {}
  
  with open(file_path) as f:
    gage_data = json.load(f)
  gage_meta_info["gage_id"] = gage_data["river_id"]
  gage_meta_info["stations"] = []
  closest_stations = gage_data["stations"][-20:]
  for station in reversed(closest_stations):
    url = base_url.format(station["station_id"])
    response = requests.get(url)
    if len(response.text)>100:
      print(response.text)
      gage_meta_info["stations"].append({"station_id":station["station_id"], 
                                         "dist":station["dist"], "cat":"ASOS"})
    elif station["station_id"] in econet_gages:
      gage_meta_info["stations"].append({"station_id":station["station_id"], 
                                         "dist":station["dist"], "cat":"ECO"})
  return gage_meta_info

def process_asos_data(file_path, base_url):
  """
  Function that saves the ASOS data to a CSV file
  """
  with open(file_path) as f:
    gage_data = json.load(f)
  for station in gage_data["stations"]:
    if station["cat"] = "ASOS":
      response = requests.get(base_url)
      df = pd.read_csv(response.text)
      df.to_csv(gage_data["gage_id"] + "_" + gage_data["station_id"]+".csv")
