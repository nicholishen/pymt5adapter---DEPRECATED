# Introduction

`pymt5adapter` is a wrapper and drop-in replacement for the MetaTrader5 python package by MetaQuotes. The API functions return the same values from the mt5 functions, but adds the following functionality:

 - Typing hinting has been added to all functions and return objects for linting and IDE integration. Intellisense will now work now matter how nested the objects are.
 - Docstrings have been added to each function (documentation copied from mql5.com). Docs can now be accessed on the fly in the IDE. For example: `Ctrl+Q` in pycharm.
 - All params can now be called by keyword. No more positional only args.
 - Testing included compliments of `pytest`
 - A new context manager has been added to provide a more pythonic interface to the setup and tear-down of the terminal connection. The use of this context-manager can do the following: 
 
   - Ensures that `mt5.shutdown()` is always called, even if the user code throws an uncaught exception.
   - Can modify the entire behavior of the API with some simple settings:
      - Ensure the terminal has enabled auto-trading.
      - Prevents running on real account by default
      - Can automatically enable global debugging using your logger of choice
      - Can raise the custom `MT5Error `exception whenever `last_error()[0] != RES_S_OK` (off by default)


# Installation

   pip install pymt5adapter
 
The `MetaTrader5` dependency sometimes has issues installing with the `pip` version that automatically gets packaged inside of the `virualenv` environment. If cannot install `MetaTrader5` then you need to update `pip` inside of the virtualenv. From the command line within the virual environment use:

   (inside virtualenv):easy_install -U pip


# Import  
This should work with any existing `MetaTrader5` script by simply changing the `import` statement from:  
  
    import MetaTrader5 as mt5  
    
to:  
      
    import pymt5adapter as mt5  

# Context Manager

The `connected` function returns a context manager which performs all setup and tear-down and ensures that `mt5.shutdown()` is always called. 

