'''
Module for testing the watchlist object.

Created on Sunday 31st March 2024.
@author: Harry New

'''

import pytest
from ig_package import IG, Watchlist

from IG_API_Details import get_username, get_password

# - - - - - - - - - - - - - - - - -

def test_watchlist_init() -> None:
  """ Testing initialisation of a watchlist object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key="e9365a5085ccd18ccc2c2d1d91ce51ad3a6e69f8",username=username,password=password)
  # Setting watchlist enable to True.
  ig.watchlist_enable = True
  # Getting watchlist dictionary from  IG.
  watchlists_dict = ig._get_watchlists_from_IG()

  # Testing single watchlist.
  watchlist = Watchlist(watchlists_dict[0]["id"],ig)
  assert hasattr(watchlist,"id")
  assert hasattr(watchlist,"name")
  assert hasattr(watchlist,"IG_obj")
  assert hasattr(watchlist,"markets")

def test_watchlist_get_instruments() -> None:
  """ Testing getting instruments through the watchlist object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key="e9365a5085ccd18ccc2c2d1d91ce51ad3a6e69f8",username=username,password=password)
  # Setting watchlist enable to True.
  ig.watchlist_enable = True
  # Getting watchlist dictionary from  IG.
  watchlists_dict = ig._get_watchlists_from_IG()
  # Getting single watchlist.
  watchlist = Watchlist(watchlists_dict[0]["id"],ig)

  for instrument in watchlist.markets:
    assert hasattr(instrument,"IG_obj")
    assert hasattr(instrument,"epic")
    assert hasattr(instrument,"name")
    assert hasattr(instrument,"lot_size")
    assert hasattr(instrument,"type")
    assert hasattr(instrument,"market_id")
    assert hasattr(instrument,"margin")

def test_watchlist_get_instrument() -> None:
  """ Testing getting single instrument through the watchlist object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key="e9365a5085ccd18ccc2c2d1d91ce51ad3a6e69f8",username=username,password=password)
  # Setting watchlist enable to True.
  ig.watchlist_enable = True
  # Getting watchlist dictionary from  IG.
  watchlists_dict = ig._get_watchlists_from_IG()
  # Getting single watchlist.
  watchlist = Watchlist("Popular Markets",ig)

  # Testing getting single instrument.
  instrument = watchlist.markets[0]
  test_instrument = watchlist._get_instrument(name=instrument.name)
  assert test_instrument != None
  test_instrument = watchlist._get_instrument(epic=instrument.epic)
  assert test_instrument != None
  test_instrument = watchlist._get_instrument(name=instrument.name,epic=instrument.epic)
  assert test_instrument != None

def test_watchlist_adding_removing_instrument() -> None:
  """ Testing adding and removing an instrumnet to a watchlist."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key="e9365a5085ccd18ccc2c2d1d91ce51ad3a6e69f8",username=username,password=password,watchlist_enable=True)

  # Creating new watchlist.
  watchlist = ig.add_watchlist("Test Watchlist")

  # Testing adding instrument.
  instrument_epic = watchlist.add_instrument("FTSE100")
  instrument = watchlist._get_instrument(epic=instrument_epic)
  assert instrument in watchlist.markets

  # Testing removing instrument through name.
  watchlist.del_instrument(instrument_name=instrument.name)
  assert instrument not in watchlist.markets
  # Testing removing instrument through epic.
  instrument_epic = watchlist.add_instrument(instrument_name="FTSE100")
  instrument = watchlist._get_instrument(epic=instrument_epic)
  watchlist.del_instrument(epic=instrument.epic)
  assert instrument not in watchlist.markets
  # Testing removing instrument when both name and epic provided.
  instrument_epic = watchlist.add_instrument(instrument_name="FTSE100")
  instrument = watchlist._get_instrument(epic=instrument_epic)
  watchlist.del_instrument(instrument_name=instrument.name,epic=instrument.epic)
  assert instrument not in watchlist.markets

  # Deleting watchlist.
  ig.del_watchlist("Test Watchlist")

@pytest.mark.parametrize("resolution,start,end", [
  ("DAY","2024:03:24-00:00:00","2024:03:25-00:00:00"),
  ("MINUTE","2024:03:24-23:59:00","2024:03:25-00:00:00"),
  ("HOUR","2024:03:24-23:00:00","2024:03:25-00:00:00")
])
def test_watchlist_historical_data(resolution,start,end) -> None:
  """ Testing getting all historical data from watchlist."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key="e9365a5085ccd18ccc2c2d1d91ce51ad3a6e69f8",username=username,password=password)
  # Setting watchlist enable to True.
  ig.watchlist_enable = True
  # Getting watchlist dictionary from  IG.
  watchlists_dict = ig._get_watchlists_from_IG()
  # Getting single watchlist.
  watchlist = Watchlist(watchlists_dict[1]["id"],ig)

  # Getting historical data.
  historical_data = watchlist.get_all_historical_data(resolution,start,end)
  for instrument in watchlist.markets:
    assert instrument.name in historical_data.keys()