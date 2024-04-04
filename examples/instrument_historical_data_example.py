'''
Example of opening trading session and getting historical data.

Created on Thursday 4th April 2024.
@author: Harry New

'''

from ig_package import IG

# - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":

  # Opening trading session.
  username = ""
  password = ""
  ig = IG(API_key="e9365a5085ccd18ccc2c2d1d91ce51ad3a6e69f8",username=username,password=password)

  # Searching instrument.
  ftse100 = ig.search_instrument("FTSE100")

  # Getting historical data in the last week with DAY resolution.
  ftse100_weekly_data = ftse100.get_historical_prices("DAY","2024:03:28-00:00:00","2024:04:03-00:00:00")
  print(ftse100_weekly_data)
