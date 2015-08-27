#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import tweepy, time, sys, json
from datetime import datetime
from coti import create_json, write_output, get_output
from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
 
dolarjson = json.loads(get_output())
updated = datetime.strptime(dolarjson['updated'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m %H:%M')

response =  updated + "\n\n" \
            "Cambios Chaco:\n"\
            "Compra: " + "{:,}".format(dolarjson['dolarpy']['cambioschaco']['compra']).replace(',','.') + \
            " | Venta: " + "{:,}".format(dolarjson['dolarpy']['cambioschaco']['venta']).replace(',','.') + \
            "\nAlberdi:\n" \
            "Compra: " + "{:,}".format(dolarjson['dolarpy']['cambiosalberdi']['compra']).replace(',','.') +\
            " | Venta: " + "{:,}".format(dolarjson['dolarpy']['cambiosalberdi']['venta']).replace(',','.') + \
            "\nMaxicambios:\n"\
            "Compra: " + "{:,}".format(dolarjson['dolarpy']['maxicambios']['compra']).replace(',','.') + \
            " | Venta: " + "{:,}".format(dolarjson['dolarpy']['maxicambios']['venta']).replace(',','.') 

api.update_status(status=response)