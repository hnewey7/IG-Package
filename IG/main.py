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
import pandas as pd

from IG_API_Details import get_body,get_header

# - - - - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - - - - - -

class RequestHandler():
  """ Object for handling all requests sent to the IG API.
        - Ensures response is successful.
        - Limits requests sent."""
  
  def __init__(self,period):
    self.period = period # Time period between each request.
    self.previous_request_time = time.time()

  def send_request(self,url,method,headers,data=None):
    """ Sending request to the API.
        Requires url, method, headers and data."""
    while time.time() - self.previous_request_time < self.period:
      time.sleep(self.period)
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

      **NOTE: Enter your API key in IG_API_Details.py**"""

  def __init__(self) -> None:
    self.header = get_header()
    self.body = get_body()
    # Initialising request handler.
    self.request_handler = RequestHandler(2)
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
      logger.info("Previous session recovered.")
      # Open file and add headers.
      logger.info("Opening JSON of previous session:")
      with open("session_info.json", "r") as f:
        json_storage = json.load(f)
        self.header["Version"] = "1"
        self.header["CST"] = json_storage["CST"]
        self.header["X-SECURITY-TOKEN"] = json_storage["X-SECURITY-TOKEN"]
        logger.info(f"  CST : {self.header['CST']}")
        logger.info(f"  X-SECURITY-TOKEN : {self.header['X-SECURITY-TOKEN']}")

    # Sending request.
    logger.info("Requesting trading session.")
    response = self.request_handler.send_request("https://api.ig.com/gateway/deal/session","POST",headers=self.header,data=json.dumps(self.body))

    # Checking status.
    while not response.ok:
      logger.info("Trading session: DENIED")
      # Deleting previous headers.
      if "CST" in self.header.keys():
        del self.header["CST"]
      if "X-SECURITY-TOKEN" in self.header.keys():
        del self.header["X-SECURITY-TOKEN"]
      # Sending new request.
      logger.info("Requesting new trading session.")
      response = self.request_handler.send_request("https://api.ig.com/gateway/deal/session","POST",headers=self.header,data=json.dumps(self.body))

    logger.info("Trading session: APPROVED")

    # Adding CST and Token to headers.
    logger.info("Adding session tokens to header.")
    self.header["CST"] = response.headers["CST"]
    self.header["X-SECURITY-TOKEN"] = response.headers["X-SECURITY-TOKEN"]
    logger.info(f"  CST : {self.header['CST']}")
    logger.info(f"  X-SECURITY-TOKEN : {self.header['X-SECURITY-TOKEN']}")

    # Saving information to json.
    logger.info("Storing current session to JSON.")
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
    logger.info("Requesting close trading session.")
    response = self.request_handler.send_request("https://api.ig.com/gateway/deal/session","PUT",headers=self.header)
    # Reverting header after.
    del self.header["_method"]

  def get_watchlists_from_IG(self) -> dict:
    """ Getting all watchlists associated with the API key.
        Watchlists are directly from IG.
        Returns list of IG watchlists."""
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
  
  def get_watchlist_objs(self) -> list:
    """ Getting watchlists within IG Obj directly from IG API.
        Returns list of watchlist objects."""
    # Getting all watchlists from IG Group's API.
    watchlists_IG = self.get_watchlists_from_IG()
    # Creating Watchlist objects from list provided.
    watchlist_objs = []
    for watchlist_dict in watchlists_IG:
      logger.info(f"Creating watchlist object from id ({watchlist_dict['id']}).")
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
    else:
      logger.info("Watchlist cannot be added, already exists.")

  def del_watchlist(self,name:str=None,id:str=None) -> None:
    """ Deleting watchlist associated to relevant API key.
        Returns Watchlist object."""
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
    logger.info(f"Requesting all instruments for watchlist ({self.id}).")
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/watchlists/{}".format(self.id),"GET",headers=self.IG_obj.header)
    if response.ok:
      logger.info("All instruments: APPROVED.")
      return json.loads(response.text)["markets"]
    else:
      logger.info("All instruments: DENIED.")
  
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
    logger.info(f"Requesting search for market ({instrument_name}).")
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/markets?searchTerm={}".format(instrument_name),"GET",headers=self.IG_obj.header)
    instruments = json.loads(response.text)["markets"]
    top_instrument_epic = instruments[0]["epic"]
    # Sending request to add instrument to watchlist.
    logger.info(f"Adding top market ({top_instrument_epic}) to watchlist ({self.id})")
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/watchlists/{}".format(self.id),"PUT",headers=self.IG_obj.header,data=json.dumps({"epic":top_instrument_epic}))
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
    logger.info(f"Requesting instrument to be removed ({instrument['epic']}) from watchlist ({self.id}).")
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/watchlists/{}/{}".format(self.id,instrument["epic"]),"DELETE",headers=self.IG_obj.header)
    # Updating markets.
    self.markets = self.get_instruments()

# - - - - - - - - - - - - - - - - - - - - -
    
class Instrument():
  """ Object representing a single instruement from IG API.
        - Allows for collection of historical data."""
  
  def __init__(self,epic,IG_obj:IG) -> None:
    self.IG_obj = IG_obj
    # Adjusting header.
    self.IG_obj.header["Version"] = "1"
    # Sending request with epic to receive market details.
    logger.info(f"Requesting instrument details ({epic}).")
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/markets/{}".format(epic),"GET",headers=self.IG_obj.header)

    instrument_details = json.loads(response.text)["instrument"]
    self.epic = instrument_details["epic"]
    self.name = instrument_details["name"]
    self.lot_size = instrument_details["lotSize"]
    self.type = instrument_details["type"]
    self.market_id = instrument_details["marketId"]
    self.margin = instrument_details["margin"]

  def get_historical_prices(self,resolution:str,start:str,end:str) -> pd.DataFrame:
    """ Getting historical price data for the instrument from IG API.
        Requires resolution, start date and end date.
        Returns pandas dataframe containing Date, Open, High, Low and Close data."""
    # Adjusting header.
    self.IG_obj.header["Version"] = "1"
    # Requesting historical price data.
    response = self.IG_obj.request_handler.send_request("https://api.ig.com/gateway/deal/prices/{}/{}?startdate={}&enddate={}".format(self.epic,resolution,start,end),"GET",headers=self.IG_obj.header)
    # Formatting data.
    all_data = []
    for price in json.loads(response.text)["prices"]:
      single_data = [price["snapshotTime"],price["openPrice"]["bid"],price["highPrice"]["bid"],price["lowPrice"]["bid"],price["closePrice"]["bid"]]
      all_data.append(single_data)
    # Creating dataframe.
    df = pd.DataFrame(all_data, columns=['Datetime', 'Open', 'High', 'Low', 'Close'])
    return df

# - - - - - - - - - - - - - - - - - - - - -
      
if __name__ == "__main__":

  # Getting logger.
  logger.setLevel(logging.INFO)

  # Creating formatter.
  formatter = logging.Formatter(fmt="%(asctime)s:%(levelname)s:   %(message)s",datefmt="%Y-%m-%d %H:%M:%S")

  # Creating stream handler.
  stdout = logging.StreamHandler()
  stdout.setLevel(logging.INFO)
  stdout.setFormatter(formatter)
  logger.addHandler(stdout)

  logger.info("- - - - - - - - - - - - - - - - -")

  ig = IG()

  instrument = Instrument("IX.D.FTSE.DAILY.IP",ig)
  data = instrument.get_historical_prices(resolution="DAY",start="2024:01:01-00:00:00",end="2024:03:17-00:00:00")
  print(data)

  ig.close_trading_session()