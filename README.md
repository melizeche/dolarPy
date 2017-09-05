# dolarPy

* Webservice: (coti.py) Checks USD/PYG exchange rate from several sites every 10 minutes, displays in json
* TwitterBot: Reads webservice output and tweet it(in a human readable format)

#### DEMO/Webservice

http://dolar.melizeche.com/api/1.0/

#### Twitter Bot

https://twitter.com/DolarPy

#### API wrappers

* For Python https://github.com/melizeche/dolarpy-wrapper-python

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

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D


## Author

Marcelo Elizeche Landó [(@melizeche)]([https://github.com/melizeche)

## Contributors

* Diego Díaz https://github.com/berithpy
* Diego Zacarías https://github.com/zv3
* Ivan Koop https://github.com/ivankoop

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.txt](LICENSE.txt) file for details

