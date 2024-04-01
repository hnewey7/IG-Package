'''
Module for testing the instrument object.

Created on Monday 1st April 2024.
@author: Harry New

'''

import pytest
from ig_package import IG, Instrument

from src.ig_package.IG_API_Details import get_username, get_password


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
  ig = IG(API_key="e9365a5085ccd18ccc2c2d1d91ce51ad3a6e69f8",username=username,password=password)
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
  ig = IG(API_key="e9365a5085ccd18ccc2c2d1d91ce51ad3a6e69f8",username=username,password=password)
  # Getting instrument through IG object.
  instrument = ig.search_instrument("FTSE 100")

  # Testing historical data.
  historical_data = instrument.get_historical_prices("MINUTE","2024:03:24-23:59:00","2024:03:25-00:00:00")
  column_names = historical_data.columns.tolist()
  assert "Open" in column_names
  assert "High" in column_names
  assert "Low" in column_names
  assert "Close" in column_names