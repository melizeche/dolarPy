# dolarPy
Checks USD/PYG exchange rate from several sites every 10 minutes, returns json

http://dolar.melizeche.com

### Documentation in progress

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

### Crontab example

MIN HOUR DAYofMONTH MONTH DAYofWEEK PYTHONPATAH SCRIPT

So for check the exchange rate every 10 minutes between 6am and 8pm on weekdays

```*/10    6-20            * * 1-5 /home/marce/dolarPy/env/bin/python /home/marce/dolarPy/coti.py```
And for tweet the exchange rate at 8am, 12pm and 6pm on weekdays
```0      8,12,18    * * 1-5 /home/marce/dolarPy/env/bin/python /home/marce/dolarPy/single_tweet_bot.py```