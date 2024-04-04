'''
Example of creating a watchlist and adding an instrument.

Created on Thursday 4th April 2024.
@author: Harry New

'''

from ig_package import IG

# - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":

  # Opening trading session with watchlist enabled.
  username = ""
  password = ""
  ig = IG(API_key="e9365a5085ccd18ccc2c2d1d91ce51ad3a6e69f8",username=username,password=password,watchlist_enable=True)

  # Creating new watchlist.
  pullback_watchlist = ig.add_watchlist("Pullback Trading Strategy")

  if pullback_watchlist:
    # Adding some instruments.
    pullback_watchlist.add_instrument("FTSE100")
    pullback_watchlist.add_instrument("US500")
    pullback_watchlist.add_instrument("Nikkei225")

    # Checking instruments in watchlist.
    for instrument in pullback_watchlist.markets:
      print("{} ({})".format(instrument.name,instrument.epic))
    
    # Deleting watchlist.
    ig.del_watchlist("Pullback Trading Strategy")
