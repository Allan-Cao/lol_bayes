# lol_bayes - Bayes Esports API Wrapper

This library (WIP) provides an interface to make queries to the Bayes V2 API, which provides data for League of Legends esports games.
<!-- The (in progress) documentation can be found [here](). -->

## TODO:
- [] Support V2 API Authentication
- [] Deploy read the docs
- [] Rewrite EMH/Historic classes to support the new merged endpoints
- [] Rewrite tests

## Install
```
pip install bayes_lol_client
```

If you wish to install the latest development version:
```
pip install -U git+https://github.com/Allan-Cao/lol_bayes
```

## Bayes Credentials
In order to use the Bayes API, you must have login credentials for **v2**, which will be prompted the first time you use the library.
These will be stored in a file in your user config path.

## Examples (outdated)

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

## Data Docs
The full documentation on the data available can be found [here](https://docs.bayesesports.com/docs-data-portal/).

## Contributing

Contributions are always welcome!

## License

[GPLv3](https://choosealicense.com/licenses/gpl-3.0/)