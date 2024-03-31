'''
Module for testing the IG object.

Created on Sunday 24th March 2024.
@author: Harry New

'''

import pytest
import time
import requests
from ig_package import IG

from src.ig_package.IG_API_Details import get_username, get_password

# - - - - - - - - - - - - - - - - -

@pytest.mark.parametrize("iteration", [i for i in range(10)])
def test_IG_valid_connection(iteration) -> None:
  """ Testing whether IG object connects within certain amount of time."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key="378b35eaad23c3ba219e4e7b57a0c2f03a4e8bbd",username=username,password=password)
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
    ig = IG(API_key=123,username="username",password="password",watchlist_enable=True)
    # Checking invalid username and password.
    ig = IG(API_key="123",username="username",password="password",watchlist_enable=True)
    del ig

@pytest.mark.parametrize("iteration",[(i) for i in range(10)])
def test_IG_close_trading_session(iteration) -> None:
  """ Testing the close trading session within the IG object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key="378b35eaad23c3ba219e4e7b57a0c2f03a4e8bbd",username=username,password=password)
  # Checking if valid session.
  assert ig.check_trading_session()
  # Deleting object.
  del ig
  
def test_IG_get_watchlist() -> None:
  """ Testing getting watchlists through the IG object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key="378b35eaad23c3ba219e4e7b57a0c2f03a4e8bbd",username=username,password=password,watchlist_enable=True)
  # Checking if watchlists available.
  assert ig.watchlists
  for watchlist in ig.watchlists:
    assert hasattr(watchlist,"id")
    assert hasattr(watchlist,"name")
    assert hasattr(watchlist,"IG_obj")
    assert hasattr(watchlist,"markets")

def test_IG_add_watchlist() -> None:
  """ Testing adding watchlists through the IG object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key="378b35eaad23c3ba219e4e7b57a0c2f03a4e8bbd",username=username,password=password,watchlist_enable=True)
  # Creating watchlist.
  watchlist = ig.add_watchlist("Test")
  assert watchlist in ig.watchlists
  # Creating watchlist with same name.
  watchlist = ig.add_watchlist("Test")
  assert watchlist == None