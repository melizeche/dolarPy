# dolarPy
Checks USD/PYG exchange rate from several sites every 10 minutes, returns in a json

http://dolar.melizeche.com

## Install

```
git clone git@github.com:melizeche/dolarPy.git
cd dolarPy
virtualenv env
source env/bin/activate
pip install -r requirements.txt
crontab -e (add coti.py)
python cotiapp.py
```