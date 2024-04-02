'''
Module to interact with IG Group's API.

Created on Tuesday 12th March 2024.
@author: Harry New

'''
from __future__ import annotations
from typing import Union

import requests
import json
import logging
import os
from pathlib import Path
import time
from datetime import datetime
import pandas as pd

# - - - - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - - - - - -

class RequestHandler():
  """ Object for handling all requests sent to the IG API.
        - Ensures response is successful.
        - Limits requests sent."""
  
  def __init__(self,period) -> None:
    self.period = period # Time period between each request.
    self.previous_request_time = time.time()

  def send_request(self,url,method,headers,data=None) -> requests.Response:
    """ Sending request to the API.
        Requires url, method, headers, with optional data."""
    while time.time() - self.previous_request_time < self.period:
      time.sleep(self.period/10)
    else:
      self.previous_request_time = time.time()
      # Choosing method.
      if method == "POST":
        response = requests.post(url,headers=headers,data=data)
      elif method == "PUT":
        response = requests.put(url,headers=headers,data=data)
      elif method == "GET":
        response = requests.get(url,headers=headers,data=data)
      else:
        response = requests.delete(url,headers=headers,data=data)

      return response


# - - - - - - - - - - - - - - - - - - - - -

class IG():
  """ Object to interact with IG Group's API.
        - Open trading sessions.
        - Get historical data.
        - Close trading sessions.

      **NOTE: API key, username and password should be entered when initialising the IG object."""

  def __init__(self,API_key:str,username:str,password:str,watchlist_enable:bool=False) -> None:
    self.watchlist_enable = watchlist_enable
    # Defining header.
    self.header = {
      "Content-Type":"application/json; charset=UTF-8",
      "Accept":"application/json; charset=UTF-8",
      "VERSION":"2",
      "X-IG-API-KEY":API_key
    }
    # Defining body.
    self.body = {
      "identifier":username,
      "password":password
    }
    # Initialising request handler.
    self.request_handler = RequestHandler(2)
    # Opening trading session.
    response_successful = self.open_trading_session()
    # Getting all watchlists.
    if watchlist_enable and response_successful:
      self.watchlists = self.get_watchlist_objs()

  def open_trading_session(self) -> bool:
    """ Opens a IG Group trading session.
        Returns boolean if response was successful or not."""
    # Sending standard request.
    logger.info("Requesting trading session.")
    self.header["VERSION"] = "2"
    response = self.request_handler.send_request("https://api.ig.com/gateway/deal/session","POST",headers=self.header,data=json.dumps(self.body))
    if response.ok:
      self.header["CST"] = response.headers["CST"]
      self.header["X-SECURITY-TOKEN"] = response.headers["X-SECURITY-TOKEN"]
      return True
    else:
      return False

  def check_trading_session(self) -> bool:
    """ Checking if trading session active.
        Returns bool depending if session is open or not."""
    # Adjusting header.
    self.header["VERSION"] = "1"
    logger.info("Requesting active trading session.")
    response = self.request_handler.send_request("https://api.ig.com/gateway/deal/session","GET",headers=self.header)
    return response.ok
    
  def get_watchlists_from_IG(self) -> dict:
    """ Getting all watchlists associated with the API key.
        Watchlists are directly from IG.
        Returns list of IG watchlists."""
    if self.watchlist_enable:
      # Adjusting header.
      self.header["Version"] = "1"
      # Sending request.
      logger.info("Requesting all watchlists associated with API key.")
      response = self.request_handler.send_request("https://api.ig.com/gateway/deal/watchlists","GET",headers=self.header)
      if response.ok:
        logger.info("All watchlists: APPROVED")
        return json.loads(response.text)["watchlists"]
      else:
        logger.info("All watchlists: DENIED")
    else:
      logger.info("Watchlists disabled in initialisation of IG object, please enable to use this method.")
  
  def get_watchlist_objs(self) -> list:
    """ Getting watchlists within IG Obj directly from IG API.
        Returns list of watchlist objects."""
    if self.watchlist_enable:
      # Getting all watchlists from IG Group's API.
      watchlists_IG = self.get_watchlists_from_IG()
      # Creating Watchlist objects from list provided.
      watchlist_objs = []
      for watchlist_dict in watchlists_IG:
        logger.info(f"Creating watchlist object from id ({watchlist_dict['id']}).")
        watchlist_objs.append(Watchlist(watchlist_dict["id"],self))
      return watchlist_objs
    else:
      logger.info("Watchlists disabled in initialisation of IG object, please enable to use this method.")

  def get_watchlist_from_IG(self,name:str=None,id:str=None) -> dict:
    """ Getting a singular watchlist associated with the API key.
        Watchlist is directly from IG.
        Returns dictionary of IG watchlist."""
    if self.watchlist_enable:
      # Getting all watchlists.
      watchlists = self.get_watchlists_from_IG()

      for watchlist in watchlists:
        if watchlist["name"] == name or watchlist["id"] == id:
          return watchlist
      else:
        raise ValueError
    else:
      logger.info("Watchlists disabled in initialisation of IG object, please enable to use this method.")
      
  def get_watchlist_obj(self,name:str=None,id:str=None) -> Watchlist:
    """ Getting a singular Watchlist object.
        Watchlist is a Python class.
        Returns the Watchlist object."""
    if self.watchlist_enable:
      for watchlist in self.watchlists:
        if watchlist.name == name or watchlist.id == id:
          return watchlist
      else:
        return None
    else:
      logger.info("Watchlists disabled in initialisation of IG object, please enable to use this method.")

  def add_watchlist(self,name:str) -> Watchlist:
    """ Adding watchlist associated to relevant API key.
        Returns Watchlist object."""
    if self.watchlist_enable:
      # Adjusting header.
      self.header["Version"] = "1"
      # Checking if watchlist already exists.
      if not self.get_watchlist_obj(name):
        # Sending request.
        logger.info(f"Requesting new watchlist ({name}).")
        response = self.request_handler.send_request("https://api.ig.com/gateway/deal/watchlists","POST",headers=self.header,data=json.dumps({"name":name}))
        if response.ok:
          logger.info("New watchlist: APPROVED")
          # Creating watchlist object.
          watchlist = Watchlist(json.loads(response.text)["watchlistId"],self)
          self.watchlists.append(watchlist)

          return watchlist
        else:
          logger.info("New watchlist: DENIED")
          return None
      else:
        logger.info("Watchlist cannot be added, already exists.")
        return None
    else:
      logger.info("Watchlists disabled in initialisation of IG object, please enable to use this method.")

  def del_watchlist(self,name:str=None,id:str=None) -> Watchlist:
    """ Deleting watchlist associated to relevant API key.
        Returns Watchlist object."""
    if self.watchlist_enable:
      try:
        # Getting watchlist.
        watchlist_IG = self.get_watchlist_from_IG(name=name,id=id)
        watchlist_obj = self.get_watchlist_obj(name=name,id=id)
        # Adjusting header.
        self.header["Version"] = "1"
        # Sending request.
        logger.info(f"Requesting watchlist to be removed ({watchlist_IG['id']}).")
        response = self.request_handler.send_request("https://api.ig.com/gateway/deal/watchlists/{}".format(watchlist_IG["id"]),"DELETE",headers=self.header)
        # Deleting watchlist object.
        self.watchlists.remove(watchlist_obj)
        return watchlist_obj
      except:
        logger.info("Watchlist could not be removed.")
        return None
    else:
      logger.info("Watchlists disabled in initialisation of IG object, please enable to use this method.")

  def search_instrument(self,name:str) -> Instrument:
    """ Search for instrument.
        Requires string to search for.
        Returns top instrument that matches string provided."""
    # Searching for instrument.
    self.header["Version"] = "1"
    logger.info(f"Requesting search for market ({name}).")
    response = self.request_handler.send_request("https://api.ig.com/gateway/deal/markets?searchTerm={}".format(name),"GET",headers=self.header)
    instruments = json.loads(response.text)["markets"]
    top_instrument_epic = instruments[0]["epic"]
    # Creating Instrument from epic.
    instrument = Instrument(top_instrument_epic,self)
    if instrument.success:
      return instrument
    else:
      return None
# - - - - - - - - - - - - - - - - - - - - -
    
class Watchlist():
  """ Object representing IG Group API's watchlist.
      - Holds a series of financial instruments.
      - Can be used to get historical data for all."""
  
  def __init__(self,id:str,IG_obj: IG) -> None:
    # Adapting header.
    IG_obj.header["Version"] = "1"
    # Getting watchlist from IG API.
    watchlist_dict = IG_obj.get_watchlist_from_IG(id=id)
    
    self.id = watchlist_dict["id"]
    self.name = watchlist_dict["name"]
    self.IG_obj = IG_obj
    self.markets = self.get_instrument_objects()

  def get_instruments_IG(self) -> list:
    """ Getting financial instruments held within the watchlist from the IG API.
        Returns list of markets stored within watchlist."""
    # Adjusting header.
    self.IG_obj.header["Version"] = "1"
    # Sending request.
    logger.info(f"Requesting all instruments for watchlist ({self.id}).")
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/watchlists/{}".format(self.id),"GET",headers=self.IG_obj.header)
    if response.ok:
      logger.info("All instruments: APPROVED.")
      return json.loads(response.text)["markets"]
    else:
      logger.info("All instruments: DENIED.")

  def get_instrument_objects(self) -> list:
    """ Getting instrument objects of all instruments within the watchlist.
        Returns list of instrument objects."""
    # Getting instruments from IG.
    instruments_IG = self.get_instruments_IG()
    # Creating list of instruments.
    instrument_objs = []
    for instrument in instruments_IG:
      new_instrument = Instrument(instrument["epic"],self.IG_obj)
      instrument_objs.append(new_instrument) if new_instrument else None
    return instrument_objs
  
  def get_instrument(self,name:str=None,epic:str=None) -> dict:
    """ Gets instrument by name or epic.
        Returns dictionary with relevant instrument information."""
    for instrument in self.markets:
      if instrument.name == name or instrument.epic == epic:
        return instrument
  
  def add_instrument(self,instrument_name:str) -> str:
    """ Adding instrument to watchlist.
        Updates watchlist markets attribute.
        Returns instrument epic."""
    # Adjusting header.
    self.IG_obj.header["Version"] = "1"
    # Sending request for instrument.
    logger.info(f"Requesting search for market ({instrument_name}).")
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/markets?searchTerm={}".format(instrument_name),"GET",headers=self.IG_obj.header)
    instruments = json.loads(response.text)["markets"]
    top_instrument_epic = instruments[0]["epic"]
    # Sending request to add instrument to watchlist.
    logger.info(f"Adding top market ({top_instrument_epic}) to watchlist ({self.id})")
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/watchlists/{}".format(self.id),"PUT",headers=self.IG_obj.header,data=json.dumps({"epic":top_instrument_epic}))
    # Updating markets.
    self.markets = self.get_instrument_objects()
    return top_instrument_epic

  def del_instrument(self,instrument_name:str=None,epic:str=None):
    """ Deleting instrument from watchlist.
        Takes instrument name and searches watchlist for it.
        Updates watchlist markets attribute."""
    # Getting instrument.
    instrument = self.get_instrument(instrument_name,epic)
    # Adjusting header.
    self.IG_obj.header["Version"] = "1"
    # Sending request to delete instrument from watchlist.
    logger.info(f"Requesting instrument to be removed ({instrument.epic}) from watchlist ({self.id}).")
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/watchlists/{}/{}".format(self.id,instrument.epic),"DELETE",headers=self.IG_obj.header)
    # Updating markets.
    self.markets = self.get_instrument_objects()

  def get_all_historical_data(self,resolution:str,start:str,end:str) -> dict:
    """ Gets all historical data from instruments contained within the watchlist.
        Requires resolution, start date and end data.
        Returns a dictionary of all dataframes with the key being the instrument name.
        
        ***NOTE: Resolution is in format SECOND, MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH ***"""
    # Creating dictionary to store all dataframes.
    df_dict = {}
    for instrument in self.markets:
      df = instrument.get_historical_prices(resolution=resolution,start=start,end=end)
      df_dict[instrument.name] = df
    return df_dict

# - - - - - - - - - - - - - - - - - - - - -
    
class Instrument():
  """ Object representing a single instruement from IG API.
        - Allows for collection of historical data."""
  
  def __init__(self,epic:str,IG_obj:IG) -> None:
    try:
      self.IG_obj = IG_obj
      # Adjusting header.
      self.IG_obj.header["Version"] = "1"
      # Sending request with epic to receive market details.
      logger.info(f"Requesting instrument details ({epic}).")
      response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/markets/{}".format(epic),"GET",headers=self.IG_obj.header)

      if response.ok:
        instrument_details = json.loads(response.text)["instrument"]
        self.success = True
        self.epic = instrument_details["epic"]
        self.name = instrument_details["name"]
        self.lot_size = instrument_details["lotSize"]
        self.type = instrument_details["type"]
        self.market_id = instrument_details["marketId"]
        self.margin = instrument_details["margin"]
      else:
        self.success = False
    except:
      logger.info("Failed to get instrument.")
      self.success = False

  def get_historical_prices(self,resolution:str,start:str,end:str) -> pd.DataFrame:
    """ Getting historical price data for the instrument from IG API.
        Requires resolution, start date and end date.
        Returns pandas dataframe containing Date, Open, High, Low and Close data."""
    # Adjusting header.
    self.IG_obj.header["Version"] = "1"
    # Requesting historical price data.
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/prices/{}/{}?startdate={}&enddate={}".format(self.epic,resolution,start,end),"GET",headers=self.IG_obj.header)
    
    # Checking if token allowance exceeded.
    if response.status_code == "403":
      logger.info("Unable to get historical data.")
      return None
    # Formatting data.
    all_data = []
    for price in json.loads(response.text)["prices"]:
      datetime_obj = datetime.strptime(price["snapshotTime"],"%Y:%m:%d-%H:%M:%S")
      single_data = [datetime_obj,price["openPrice"]["bid"],price["highPrice"]["bid"],price["lowPrice"]["bid"],price["closePrice"]["bid"]]
      all_data.append(single_data)
    # Creating dataframe.
    df = pd.DataFrame(all_data, columns=['Datetime', 'Open', 'High', 'Low', 'Close'])
    df.set_index("Datetime",inplace=True)
    return df

# - - - - - - - - - - - - - - - - - - - - -
