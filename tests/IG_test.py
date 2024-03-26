'''
Module for testing the IG object.

Created on Sunday 24th March 2024.
@author: Harry New

'''

import pytest
import time
import requests
from ig_package import IG

# - - - - - - - - - - - - - - - - -

@pytest.mark.parametrize("expected_time", [(60 - i * 6) for i in range(10)])
def test_IG_valid_connection(expected_time) -> None:
  """ Testing whether IG object connects within certain amount of time."""
  start_time = time.time()
  # Initialising IG object.
  ig = IG(API_key="32691aee9bc9e003ccc8045982d8aa73de86ad69",username="",password="")
  # Checking within time.
  assert time.time() - start_time < expected_time
  # Checking if valid session.
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
  # Checking invalid key type.
  with pytest.raises(requests.exceptions.InvalidHeader):
    ig = IG(API_key=123,username="username",password="password",watchlist_enable=True)
  # Checking invalid username and password.
  with pytest.raises(TimeoutError):
    ig = IG(API_key="123",username="username",password="password",watchlist_enable=True)

