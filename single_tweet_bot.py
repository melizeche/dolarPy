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
updated = datetime.strptime(dolarjson['updated'], '%Y-%m-%d %H:%M:%S').strftime('📅 %d/%m ⏳%H:%M')

response =  updated + "\n\n" \
            "💱\n■ Cambios Chaco:\n"\
            "Compra: " + "{:,}".format(dolarjson['dolarpy']['cambioschaco']['compra']).replace(',','.')[:-2] + \
            " | Venta: " + "{:,}".format(dolarjson['dolarpy']['cambioschaco']['venta']).replace(',','.')[:-2] + \
            "\n■ Mundial:\n" \
            "Compra: " + "{:,}".format(dolarjson['dolarpy']['mundialcambios']['compra']).replace(',','.')[:-2] + \
            " | Venta: " + "{:,}".format(dolarjson['dolarpy']['mundialcambios']['venta']).replace(',','.')[:-2] + \
            "\n■ MyD Cambios:\n" \
            "Compra: " + "{:,}".format(dolarjson['dolarpy']['mydcambios']['compra']).replace(',','.')[:-2] + \
            " | Venta: " + "{:,}".format(dolarjson['dolarpy']['mydcambios']['venta']).replace(',','.')[:-2] + \
            "\n■ Maxicambios:\n" \
            "Compra: " + "{:,}".format(dolarjson['dolarpy']['maxicambios']['compra']).replace(',','.')[:-2] + \
            " | Venta: " + "{:,}".format(dolarjson['dolarpy']['maxicambios']['venta']).replace(',','.')[:-2] + \
            "\n\n🏛\n■ BCP:\n"\
            "Compra: " + "{:,}".format(int(dolarjson['dolarpy']['bcp']['compra'])).replace(',','.') + \
            " | Venta: " + "{:,}".format(int(dolarjson['dolarpy']['bcp']['venta'])).replace(',','.') + \
            "\n■ SET:\n" \
            "Compra: " + "{:,}".format(int(dolarjson['dolarpy']['set']['compra'])).replace(',','.') +\
            " | Venta: " + "{:,}".format(int(dolarjson['dolarpy']['set']['venta'])).replace(',','.')

api.update_status(status=response)

try:  # Mastodon integration
    from mastodon import Mastodon
    from config import MASTODON_ACCESS_TOKEN, MASTODON_API_BASE

    mastodon = Mastodon(access_token=MASTODON_ACCESS_TOKEN, api_base_url = MASTODON_API_BASE)

    mastodon.status_post(response, language='es')

except Exception as e:
    print(e)
