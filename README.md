# dolarPy
Checks USD/PYG exchange rate from several sites, with a calculator, RESTful API and a twitter bot

* [Scraper: ](coti.py) Checks USD/PYG exchange rate from several sites every 10 minutes, saves the info in a json file
* [Webservice: ](cotiapp.py) Flask app to serve the API and display the main website with the calculator
* [TwitterBot: ](single_tweet_bot.py) Reads the webservice output and tweet it(in a human readable format)

#### DEMO/Webservice

http://dolar.melizeche.com/api/1.0/

#### Twitter Bot

https://twitter.com/DolarPy

#### Mobile

* For Android  https://github.com/ivankoop/DolarPy-Android

#### API wrappers

* For Java https://github.com/melizeche/dolarpy-wrapper-java
* For Python https://github.com/melizeche/dolarpy-wrapper-python

## Documentation in progress

## Requirements

* Python 2.7+ or 3.5+
* BeautifulSoup4
* Flask
* Tweepy

## Install

```
git clone git@github.com:melizeche/dolarPy.git
cd dolarPy
python3 -m venv env
# if venv module is not installed install with `sudo apt install python3-venv`
source env/bin/activate
pip install -r requirements.txt
crontab -e (add coti.py) // See example below
python cotiapp.py
```
### On macOS High Sierra with python3 (also most linux distros)

```
# pip3 is installed with Python3
pip3 install virtualenv
# creating the virtualenv
virtualenv -p python3 env
# activate the virtualenv:
source env/bin/activate
pip3 install -r requirements.txt
# and the run
# if you need to deactivate the virtualenv:
deactivate
```

### Crontab format and example

MIN 	HOUR 	DAYofMONTH 	MONTH 	DAYofWEEK 	PYTHONPATH SCRIPT

So for check/update the exchange rate every 10 minutes between 6am and 8pm on weekdays

```*/10    6-20            * * 1-5 /apps/dolarPy/env/bin/python /apps/dolarPy/coti.py```

And for tweet the exchange rate at 8am, 12pm and 6pm on weekdays

```0      8,12,18    * * 1-5 /apps/dolarPy/env/bin/python /apps/dolarPy/single_tweet_bot.py```

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Author

* Marcelo Elizeche Landó https://github.com/melizeche

## Contributors / Thanks

* Alejo Carballude https://github.com/AlejoAsd
* Carlos Carvallo https://github.com/carloscarvallo
* Carlos Laspina https://github.com/claspina
* Carlos Vallejos  https://github.com/cabupy
* Christian Zelaya https://github.com/eduzetapy
* Diego Díaz https://github.com/berithpy
* Diego Zacarías https://github.com/zv3
* Ivan Koop https://github.com/ivankoop
* Mauricio Medina https://github.com/mauri-medina
* Taras Samoilenko https://github.com/cos1715

## TODO(APIv2)

* ~Better~ Documentation
* Add more currencies
* Databases support
* Historical data API endpoint

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.txt](LICENSE.txt) file for details

