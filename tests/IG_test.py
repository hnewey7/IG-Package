'''
Module for testing the IG object.

Created on Sunday 24th March 2024.
@author: Harry New

'''

import pytest
import requests
from ig_package import IG

from IG_API_Details import get_username, get_password, get_key, get_account_type, get_account_number

# - - - - - - - - - - - - - - - - -

@pytest.mark.parametrize("iteration", [i for i in range(10)])
def test_IG_valid_connection(iteration) -> None:
  """ Testing whether IG object connects within certain amount of time."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key=get_key(),username=username,password=password,acc_type=get_account_type(),acc_number=get_account_number())
  # Checking trading session.
  assert ig.check_trading_session()
  # Deleting object.
  del ig
  
@pytest.mark.parametrize("API_key,username,password,watchlist_enable", [
  (123,"how","are",True),
  ("Hey",123,"are",True),
  ("Hey","how",123,True)
])
def test_IG_invalid_connection(API_key,username,password,watchlist_enable) -> None:
  """ Testing IG object connection with a series of false values and types."""
  with pytest.raises(requests.exceptions.InvalidHeader):
    # Checking invalid key type.
    ig = IG(API_key=123,username="username",password="password",acc_type="",acc_number="",watchlist_enable=True)
    # Checking invalid username and password.
    ig = IG(API_key="123",username="username",password="password",acc_type="",acc_number="",watchlist_enable=True)
    del ig

@pytest.mark.parametrize("iteration",[(i) for i in range(10)])
def test_IG_close_trading_session(iteration) -> None:
  """ Testing the close trading session within the IG object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key=get_key(),username=username,password=password,acc_type=get_account_type(),acc_number=get_account_number())
  # Checking if valid session.
  assert ig.check_trading_session()
  # Deleting object.
  del ig
  
def test_IG_watchlist_enabled() -> None:
  """ Testing watchlists through the IG object.
        - Enables watchlist and checks valid attributes.
        - Adds watchlist, checks for return and null return when already present.
        - Deletes watchlist and tries deleting watchlist when not present."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key=get_key(),username=username,password=password,acc_type=get_account_type(),acc_number=get_account_number(),watchlist_enable=True)
  # Checking if watchlists available.
  assert ig.watchlists
  for watchlist in ig.watchlists:
    assert hasattr(watchlist,"id")
    assert hasattr(watchlist,"name")
    assert hasattr(watchlist,"IG_obj")
    assert hasattr(watchlist,"markets")

  # Checking if watchlist exists.
  for watchlist in ig.watchlists:
    if watchlist.name == "Test":
      ig.del_watchlist(name=watchlist.name)
      
  # Creating watchlist.
  watchlist = ig.add_watchlist("Test")
  assert watchlist in ig.watchlists
  # Creating watchlist with same name.
  watchlist = ig.add_watchlist("Test")
  assert watchlist in ig.watchlists

  # Deleting watchlist through name.
  watchlist = ig.del_watchlist("Test")
  assert watchlist not in ig.watchlists
  # Deleting watchlist through id.
  watchlist = ig.add_watchlist("Test")
  watchlist = ig.del_watchlist(id=watchlist.id)
  assert watchlist not in ig.watchlists
  # Deleting when both parameters provided.
  watchlist = ig.add_watchlist("Test")
  watchlist = ig.del_watchlist(name=watchlist.name,id=watchlist.id)
  assert watchlist not in ig.watchlists

  # Deleting false watchlist.
  watchlist = ig.del_watchlist("Test")
  assert watchlist == None
  watchlist = ig.del_watchlist(id="837482489792uhs")
  assert watchlist == None
  watchlist = ig.del_watchlist("Test",id="837482489792uhs")
  assert watchlist == None

def test_IG_watchlist_disabled() -> None:
  """ Testing watchlist methods if disabled through IG object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key=get_key(),username=username,password=password,acc_type=get_account_type(),acc_number=get_account_number())
  
  # Testing getting watchlists from IG.
  watchlists_dict = ig._get_watchlists_from_IG()
  assert watchlists_dict == None
  # Testing getting watchlist objects.
  watchlists = ig._get_watchlist_objs()
  assert watchlists == None
  # Testing getting single watchlist.
  watchlist_dict = ig._get_watchlist_from_IG()
  assert watchlist_dict == None
  # Testing getting single watchlist object.
  watchlist = ig._get_watchlist_obj()
  assert watchlist == None
  # Testing adding watchlist.
  watchlist = ig.add_watchlist("Test")
  assert watchlist == None
  # Testing deleting watchlist.
  watchlist = ig.del_watchlist("Test")
  assert watchlist == None

def test_IG_search_instrument() -> None:
  """ Testing searching an instrument through the IG object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key=get_key(),username=username,password=password,acc_type=get_account_type(),acc_number=get_account_number())
  # Searching for instrument.
  instrument = ig.search_instrument("FTSE100")
  assert hasattr(instrument,"IG_obj")
  assert hasattr(instrument,"epic")
  assert hasattr(instrument,"name")
  assert hasattr(instrument,"lot_size")
  assert hasattr(instrument,"type")
  assert hasattr(instrument,"market_id")
  assert hasattr(instrument,"margin")

def test_IG_open_streaming_session() -> None:
  """ Testing the open a streaming session method."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key=get_key(),username=username,password=password,acc_type=get_account_type(),acc_number=get_account_number())
  # Handling checks.
  assert not hasattr(ig,"ig_service")
  assert not hasattr(ig,"ig_streaming_service")
  assert not hasattr(ig,"streaming_manager")
  # Opening streamin g session.
  ig.open_streaming_session()
  # Handling checks.
  assert hasattr(ig,"ig_service")
  assert hasattr(ig,"ig_streaming_service")
  assert hasattr(ig,"streaming_manager")