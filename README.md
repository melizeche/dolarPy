# dolarPy

* Webservice: (coti.py) Checks USD/PYG exchange rate from several sites every 10 minutes, displays in json
* TwitterBot: Reads webservice output and tweet it(in a human readable format)

#### DEMO/Webservice

http://dolar.melizeche.com/api/1.0/

#### Twitter Bot

https://twitter.com/DolarPy

## Documentation in progress

## Requirements

* Python 2.7+
* BeautifulSoup4
* Flask
* Tweepy

## Install

```
git clone git@github.com:melizeche/dolarPy.git
cd dolarPy
virtualenv env
source env/bin/activate
pip install -r requirements.txt
crontab -e (add coti.py) // See example below
python cotiapp.py
```

### Crontab format and example

MIN 	HOUR 	DAYofMONTH 	MONTH 	DAYofWEEK 	PYTHONPATH SCRIPT

So for check/update the exchange rate every 10 minutes between 6am and 8pm on weekdays

```*/10    6-20            * * 1-5 /apps/dolarPy/env/bin/python /apps/dolarPy/coti.py```

And for tweet the exchange rate at 8am, 12pm and 6pm on weekdays

```0      8,12,18    * * 1-5 /apps/dolarPy/env/bin/python /apps/dolarPy/single_tweet_bot.py```
