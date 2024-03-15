'''
Module to interact with IG Group's API.

Created on Tuesday 12th March 2024.
@author: Harry New

'''

import requests
import json
import logging
import os
from pathlib import Path
import time

from IG_API_Details import get_body,get_header

# - - - - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - - - - - -

class IG():
  """ Object to interact with IG Group's API.
        - Open trading sessions.
        - Get historical data.
        - Close trading sessions.

      **NOTE: Enter your API key in IG_API_Details.py**"""

  def __init__(self) -> None:
    self.header = get_header()
    self.body = get_body()
    # Opening trading session.
    self.open_trading_session()
    # Getting all watchlists.
    self.watchlists = self.get_watchlist_objs()

  def open_trading_session(self) -> None:
    """ Opens a IG Group trading session.
        - Checks if previous session open.
        - Saves session details to JSON file for future use.
        - Requests new session if expired or no previous session."""
    # Checking if previous session.
    if os.path.exists(os.getcwd() + "\\session_info.json"):
      # Open file and add headers.
      with open("session_info.json", "r") as f:
        json_storage = json.load(f)
        self.header["Version"] = "1"
        self.header["CST"] = json_storage["CST"]
        self.header["X-SECURITY-TOKEN"] = json_storage["X-SECURITY-TOKEN"]

    # Sending request.
    response = requests.post("https://api.ig.com/gateway/deal/session",headers=self.header,data=json.dumps(self.body))

    # Checking status.
    while not response.ok:
      # Deleting previous headers.
      if "CST" in self.header.keys():
        del self.header["CST"]
      if "X-SECURITY-TOKEN" in self.header.keys():
        del self.header["X-SECURITY-TOKEN"]
      # Sending new request.
      response = requests.post("https://api.ig.com/gateway/deal/session",headers=self.header,data=json.dumps(self.body))
      time.sleep(2)

    # Adding CST and Token to headers.
    self.header["CST"] = response.headers["CST"]
    self.header["X-SECURITY-TOKEN"] = response.headers["X-SECURITY-TOKEN"]

    # Saving information to json.
    json_storage = {}
    json_storage["CST"] = self.header["CST"]
    json_storage["X-SECURITY-TOKEN"] = self.header["X-SECURITY-TOKEN"]
    json_storage = json.dumps(json_storage)
    with open("session_info.json", "w") as f:
      f.write(json_storage)
    
  def close_trading_session(self) -> None:
    """ Close the active trading session."""
    # Adjusting header.
    self.header["Version"] = "1"
    self.header["_method"] = "DELETE"
    # Sending request.
    response = requests.put("https://api.ig.com/gateway/deal/session",headers=self.header)
    # Reverting header after.
    del self.header["_method"]

  def get_watchlists_from_IG(self) -> dict:
    """ Getting all watchlists associated with the API key.
        Watchlists are directly from IG.
        Returns list of IG watchlists."""
    # Adjusting header.
    self.header["Version"] = "1"
    # Sending request.
    response = requests.get("https://api.ig.com/gateway/deal/watchlists",headers=self.header)
    return json.loads(response.text)["watchlists"]
  
  def get_watchlist_objs(self) -> list:
    """ Getting watchlists within IG Obj directly from IG API.
        Returns list of watchlist objects."""
    # Getting all watchlists from IG Group's API.
    watchlists_IG = self.get_watchlists_from_IG()
    # Creating Watchlist objects from list provided.
    watchlist_objs = []
    for watchlist_dict in watchlists_IG:
      watchlist_objs.append(Watchlist(watchlist_dict["id"],self))
    return watchlist_objs

  def get_watchlist_from_IG(self,name:str=None,id:str=None) -> dict:
    """ Getting a singular watchlist associated with the API key.
        Watchlist is directly from IG.
        Returns dictionary of IG watchlist."""
    # Getting all watchlists.
    watchlists = self.get_watchlists_from_IG()

    for watchlist in watchlists:
      if watchlist["name"] == name or watchlist["id"] == id:
        return watchlist
      
  def get_watchlist_obj(self,name:str=None,id:str=None):
    """ Getting a singular Watchlist object.
        Watchlist is a Python class.
        Returns the Watchlist object."""
    for watchlist in self.watchlists:
      if watchlist.name == name or watchlist.id == id:
        return watchlist

  def add_watchlist(self,name:str):
    """ Adding watchlist associated to relevant API key.
        Returns Watchlist object."""
    # Adjusting header.
    self.header["Version"] = "1"
    # Checking if watchlist already exists.
    if not self.get_watchlist_obj(name):
      # Sending request.
      response = requests.post("https://api.ig.com/gateway/deal/watchlists",headers=self.header,data=json.dumps({"name":name}))
      # Creating watchlist object.
      watchlist = Watchlist(json.loads(response.text)["watchlistId"],self)
      self.watchlists.append(watchlist)

      return watchlist
    else:
      logger.info("Watchlist cannot be added, already exists.")

  def del_watchlist(self,name:str=None,id:str=None) -> None:
    """ Deleting watchlist associated to relevant API key.
        Returns Watchlist object."""
    # Getting watchlist.
    if name:
      watchlist_IG = self.get_watchlist_from_IG(name=name)
      watchlist_obj = self.get_watchlist_obj(name=name)
    else:
      watchlist_IG = self.get_watchlist_from_IG(id=id)
      watchlist_obj = self.get_watchlist_obj(id=id)
    # Adjusting header.
    self.header["Version"] = "1"
    # Sending request.
    response = requests.delete("https://api.ig.com/gateway/deal/watchlists/{}".format(watchlist_IG["id"]),headers=self.header)
    # Deleting watchlist object.
    self.watchlists.remove(watchlist_obj)

# - - - - - - - - - - - - - - - - - - - - -
    
class Watchlist():
  """ Object representing IG Group API's watchlist.
      - Holds a series of financial instruments.
      - Can be used to get historical data for all."""
  
  def __init__(self,id,IG_obj: IG) -> None:
    # Adapting header.
    IG_obj.header["Version"] = "1"
    # Getting watchlist from IG API.
    watchlist_dict = IG_obj.get_watchlist_from_IG(id=id)
    
    self.id = watchlist_dict["id"]
    self.name = watchlist_dict["name"]
    self.IG_obj = IG_obj
    self.markets = self.get_instruments()

  def get_instruments(self) -> list:
    """ Getting financial instruments held within the watchlist.
        Returns list of markets stored within watchlist."""
    # Adjusting header.
    self.IG_obj.header["Version"] = "1"
    # Sending request.
    response = requests.get("https://api.ig.com/gateway/deal/watchlists/{}".format(self.id),headers=self.IG_obj.header)
    return json.loads(response.text)["markets"]
  
  def get_instrument(self,name:str=None,epic:str=None) -> dict:
    """ Gets instrument by name or epic.
        Returns dictionary with relevant instrument information."""
    for instrument in self.markets:
      if instrument["instrumentName"] == name or instrument["epic"] == epic:
        return instrument
  
  def add_instrument(self,instrument_name:str):
    """ Adding instrument to watchlist.
        Updates watchlist markets attribute."""
    # Adjusting header.
    self.IG_obj.header["Version"] = "1"
    # Sending request for instrument.
    response = requests.get("https://api.ig.com/gateway/deal/markets?searchTerm={}".format(instrument_name),headers=self.IG_obj.header)
    instruments = json.loads(response.text)["markets"]
    top_instrument_epic = instruments[0]["epic"]
    # Sending request to add instrument to watchlist.
    response = requests.put("https://api.ig.com/gateway/deal/watchlists/{}".format(self.id),headers=self.IG_obj.header,data=json.dumps({"epic":top_instrument_epic}))
    # Updating markets.
    self.markets = self.get_instruments()

  def del_instrument(self,instrument_name:str=None,epic:str=None):
    """ Deleting instrument from watchlist.
        Takes instrument name and searches watchlist for it.
        Updates watchlist markets attribute."""
    # Getting instrument.
    instrument = self.get_instrument(instrument_name,epic)
    # Adjusting header.
    self.IG_obj.header["Version"] = "1"
    # Sending request to delete instrument from watchlist.
    response = requests.delete("https://api.ig.com/gateway/deal/watchlists/{}/{}".format(self.id,instrument["epic"]),headers=self.IG_obj.header)
    # Updating markets.
    self.markets = self.get_instruments()

# - - - - - - - - - - - - - - - - - - - - -
      
if __name__ == "__main__":

  ig = IG()

  new_watchlist = ig.add_watchlist("Test")
  print(new_watchlist.markets) 
  new_watchlist.add_instrument("FTSE 100")
  print(new_watchlist.markets) 
  new_watchlist.del_instrument("FTSE 100")
  print(new_watchlist.markets) 
  ig.del_watchlist("Test")

  ig.close_trading_session()