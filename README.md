# Bayes LoL Client

This library is used to make queries to the Bayes EMH API, which provides data for League of Legends esports games.
The (in progress) documentation can be found [here](https://bayes-lol-client.readthedocs.io).

## Install
```
pip install bayes_lol_client
```

If you wish to install the latest development version:
```
pip install -U git+https://github.com/arbolitoloco1/bayes_lol_client
```

## Bayes Credentials
In order to use the Bayes API, you must have login credentials, which will be prompted the first time you use the library.
These will be stored in a file in your user config path.

## Examples

### Get both the summary and details files, as dicts, for a given game ID:
````python
from bayes_lol_client import BayesEMH

emh = BayesEMH()

summary, details = emh.get_game_data("ESPORTSTMNT02_3211754")
````

### Get a list of all available tags on EMH, but providing the credentials when initializing the class:
````python
from bayes_lol_client import BayesEMH

emh = BayesEMH(username="user_test", password="secretpassword123")

tags = emh.get_tags_list()
````

## EMH Docs
The full documentation to use EMH can be found [here](https://docs.bayesesports.com/api/emh_riot).