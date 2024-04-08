# Python Package for IG Group's API.

## A package allowing easy interaction with IG Group's REST API.

This project is a fully functional package that allows easy interaction with IG Group's REST API. The main function being to retrieve historical data for later use in backtesting. To do this, key functions were defined for:

* Opening trading sessions.
* Searching specific financial instruments.
* Getting historical prices from finanical instruments.
* Managing watchlists.
* Closing trading sessions.

![Class diagram](https://github.com/hnewey7/IG-Package/blob/main/class_diagram.png?raw=true)

## How to utilise this package

1. Use ```pip install ig_package``` in the command prompt.
2. Import the IG object into your script:
   ```python
   from ig_package import IG
   ```
3. Initialise the IG object including your API Key and details in the relevant parameters.

## How to contribute to this package

The classes within this package are based on the functionaliy of IG Group's REST API so in order to contribute I would recommend experimenting with their [API Companion](https://labs.ig.com/sample-apps/api-companion/index.html). 

The three main classes: IG, Watchlist and Instrument, are all defined in [main.py](/IG/main.py) and functions can be easily added to each of them.

If any new classes have been defined then remember to import the new classes into [\_\_init__.py](/IG/__init__.py). This allows users to import the classes directly from the package.

## Fixing bugs

Please make sure to report any bugs found as issues on Github. If you then want to submit a pull request, make sure to reference the issue.

## Future Development

1. Adding functions to handle active positions, therefore allowing users to execute trades.
2. Adding working trades so executing trades when the price reaches a certain amount on a specific instrument.
3. Adding a demo version as IG's API also can manage demo accounts too.