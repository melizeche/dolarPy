#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import requests

from decimal import Decimal
from bs4 import BeautifulSoup
from datetime import datetime
from websocket import create_connection

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def format_decimal(number):
    return str(number).replace('.', '').replace(',', '.')


def chaco():
    try:
        soup = json.loads(
            requests.get('http://www.cambioschaco.com.py/api/branch_office/1/exchange', timeout=10).text)
        compra = soup['items'][0]['purchasePrice']
        venta = soup['items'][0]['salePrice']
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def maxi():
    today = datetime.today().strftime('%d%m%Y')
    url = "http://www.maxicambios.com.py/Umbraco/api/Pizarra/Cotizaciones?fecha=%s" % (
        today)
    try:
        soup = requests.get(url, timeout=10).json()
        compra = soup[0]['Compra']
        venta = soup[0]['Venta']
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def alberdi():
    try:
        ws = create_connection("ws://cambiosalberdi.com:9300")
        ws.send("Connected")
        result = ws.recv()
        soup = json.loads(result)
        compra = soup['asuncion'][0]['compra'].replace('.', '')
        venta = soup['asuncion'][0]['venta'].replace('.', '')
        ws.close()
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def bcp():
    try:
        soup = BeautifulSoup(
            requests.get('https://www.bcp.gov.py/webapps/web/cotizacion/monedas', timeout=10,
                         headers={'user-agent': 'Mozilla/5.0'}, verify=False).text, "html.parser")
        ref = soup.select(
            '#cotizacion-interbancaria > tbody > tr > td:nth-of-type(4)')[0].get_text()
        ref = ref.replace('.', '').replace(',', '.')
        soup = BeautifulSoup(
            requests.get('https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante', timeout=10,
                         headers={'user-agent': 'Mozilla/5.0'}, verify=False).text, "html.parser")
        compra_array = soup.find(
            class_="table table-striped table-bordered table-condensed").select('tr > td:nth-of-type(4)')
        venta_array = soup.find(
            class_="table table-striped table-bordered table-condensed").select('tr > td:nth-of-type(5)')
        posicion = len(compra_array) - 1
        compra = compra_array[posicion].get_text(
        ).replace('.', '').replace(',', '.')
        venta = venta_array[posicion].get_text().replace(
            '.', '').replace(',', '.')
    except requests.ConnectionError:
        compra, venta, ref = 0, 0, 0
    except:
        compra, venta, ref = 0, 0, 0

    return Decimal(compra), Decimal(venta), Decimal(ref)


def setgov():
    try:
        soup = BeautifulSoup(
            requests.get('http://www.set.gov.py/portal/PARAGUAY-SET', timeout=10).text, "html.parser")
        compra = soup.find_all(class_="UITipoGrafiaCotizacion")[0].select('div')[
            1].contents[4].replace('.', '').replace(',', '.')
        venta = soup.find_all(class_="UITipoGrafiaCotizacion")[0].select('div')[
            2].contents[4].replace('.', '').replace(',', '.')
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def interfisa():
    try:
        soup = BeautifulSoup(
            requests.get('https://www.interfisa.com.py', timeout=8).text, "html.parser")
        compra = soup.find_all(
            id="dolar_compra")[0].string.replace('.', '')
        venta = soup.find_all(
            id="dolar_venta")[0].string.replace('.', '')
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def amambay():
    try:
        soup = requests.get(
            "http://www.bancoamambay.com.py/ebanking_ext/api/data/currency_exchange", timeout=10).json()
        compra = soup['currencyExchanges'][0]['purchasePrice']
        venta = soup['currencyExchanges'][0]['salePrice']
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def myd():
    try:
        soup = BeautifulSoup(
            requests.get('https://www.mydcambios.com.py/', timeout=10).text, "html.parser")
        compra = soup.select('#cotizaciones > div > table > tbody')[
            0].findAll('td')[1].text.replace(',', '')
        venta = soup.select('#cotizaciones > div > table > tbody')[
            0].findAll('td')[2].text.replace(',', '')
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def create_json():
    mcompra, mventa = maxi()
    ccompra, cventa = chaco()
    acompra, aventa = alberdi()
    bcpcompra, bcpventa, bcpref = bcp()
    setcompra, setventa = setgov()
    intcompra, intventa = interfisa()
    ambcompra, ambventa = amambay()
    mydcompra, mydventa = myd()
    respjson = {
        'dolarpy': {
            'cambiosalberdi': {
                'compra': acompra,
                'venta': aventa
            },
            'cambioschaco': {
                'compra': ccompra,
                'venta': cventa
            },
            'maxicambios': {
                'compra': mcompra,
                'venta': mventa
            },
            'bcp': {
                'compra': bcpcompra,
                'venta': bcpventa,
                'referencial_diario': bcpref
            },
            'set': {
                'compra': setcompra,
                'venta': setventa
            },
            'interfisa': {
                'compra': intcompra,
                'venta': intventa
            },
            'amambay': {
                'compra': ambcompra,
                'venta': ambventa
            },
            'mydcambios': {
                'compra': mydcompra,
                'venta': mydventa
            }
        },
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return json.dumps(respjson, indent=4, sort_keys=True, separators=(',', ': '), default=decimal_default)


def get_output():
    with open('dolar.json', 'r') as f:
        response = f.read()
    return response


def write_output():
    response = create_json()
    with open('dolar.json', 'w') as f:
        f.write(response)


write_output()
