'''
Script for initially performing a backtesting strategy.

Created on Saturday 24th February 2024.
@author: Harry.New

'''

import pandas as pd
import requests
import backtesting
import traceback
import json

from IG.IG_API_Details import get_body,get_header

# - - - - - - - - - - - - - - - - - - -

def create_trading_session(header,body) -> dict:
  try:
    # Sending request.
    response = requests.post("https://api.ig.com/gateway/deal/session",headers=header,data=json.dumps(body))
    # Adding CST and Token to headers.
    print(response.headers["CST"])
    print(response.headers["X-SECURITY-TOKEN"])
    header["CST"] = response.headers["CST"]
    header["X-SECURITY-TOKEN"] = response.headers["X-SECURITY-TOKEN"]
    return header
  except Exception:
    traceback.print_exc()

def get_historical_data(header):
  try:
    # Sending request.
    print(header)
    header["Version"] = "3"
    response = requests.get("https://api.ig.com/gateway/deal/prices/IX.D.FTSE.DAILY.IP",headers=header)
    print(response.text)
  except Exception:
    traceback.print_exc()

# - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
  
  # Getting header and body for request.
  header = get_header()
  body = get_body()

  header = create_trading_session(header,body)

  get_historical_data(header)

