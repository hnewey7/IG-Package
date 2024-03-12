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

from IG_API_Details import get_body,get_header

# - - - - - - - - - - - - - - - - - - -

def create_trading_session():
  try:
    # Getting header and body.
    header = get_header()
    body = get_body()
    # Sending request.
    response = requests.post("https://api.ig.com/gateway/deal/session",headers=header,data=json.dumps(body))
    print(response)
    print(response.headers["CST"])
    print(response.headers["X-SECURITY-TOKEN"])
  except Exception:
    traceback.print_exc()

# - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
  create_trading_session()