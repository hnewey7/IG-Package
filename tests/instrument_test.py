'''
Module for testing the instrument object.

Created on Monday 1st April 2024.
@author: Harry New

'''

import pytest
from ig_package import IG, Instrument

from IG_API_Details import get_username, get_password, get_key


# - - - - - - - - - - - - - - - - -

@pytest.mark.parametrize("instrument", [
  ("FTSE 100"),
  ("US500"),
  ("UK 100"),
  ("DOW")
])
def test_instrument_init(instrument) -> None:
  """ Testing initialisation of the instrument object."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key=get_key(),username=username,password=password)
  # Getting instrument through IG object.
  instrument = ig.search_instrument(instrument)

  assert hasattr(instrument,"IG_obj")
  assert hasattr(instrument,"epic")
  assert hasattr(instrument,"name")
  assert hasattr(instrument,"lot_size")
  assert hasattr(instrument,"type")
  assert hasattr(instrument,"market_id")
  assert hasattr(instrument,"margin")

def test_instrument_historical_prices() -> None:
  """ Testing getting historical prices of an instrument."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key=get_key(),username=username,password=password)
  # Getting instrument through IG object.
  instrument = ig.search_instrument("FTSE 100")

  # Testing historical data.
  historical_data = instrument.get_historical_prices("MINUTE","2024:03:24-23:59:00","2024:03:25-00:00:00")
  column_names = historical_data.columns.tolist()
  assert "Open" in column_names
  assert "High" in column_names
  assert "Low" in column_names
  assert "Close" in column_names

def test_instrument_start_live_data() -> None:
  """ Testing get live data method of the instrument class."""
  # Initialising IG object.
  username = get_username()
  password = get_password()
  ig = IG(API_key=get_key(),username=username,password=password)
  # Getting instrument through IG object.
  instrument = ig.search_instrument("FTSE 100")

  # Checking if streaming session not open.
  assert not hasattr(ig,"streaming_manager")
  assert not hasattr(ig,"ig_service")
  assert not hasattr(ig,"ig_streaming_service")

  # Starting collection of data.
  instrument.start_live_data()

  # Checking if streaming session open.
  assert hasattr(ig,"streaming_manager")
  assert hasattr(ig,"ig_service")
  assert hasattr(ig,"ig_streaming_service")
  assert hasattr(instrument,"ticker")