#!/usr/bin/python
import json
import requests
    
from decimal import Decimal
from bs4 import BeautifulSoup
from datetime import datetime


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def chaco():
    try:
        soup = BeautifulSoup(
            requests.get('http://www.cambioschaco.com.py/php/imprimir_.php', timeout=8).text, "html.parser")
        compra = soup.find_all('tr')[3].contents[5].string[:5].replace('.', '')
        venta = soup.find_all('tr')[3].contents[7].string[:5].replace('.', '')
    except requests.ConnectionError:
        compra, venta = 0, 0

    return int(compra), int(venta)


def maxi():
    try:
        soup = BeautifulSoup(
            requests.get('http://www.maxicambios.com.py/', timeout=8).text, "html.parser")
        compra = soup.find_all(class_='lineas1')[0].contents[
            7].string.replace('.', '')
        venta = soup.find_all(class_='lineas1')[0].contents[
            5].string.replace('.', '')
    except requests.ConnectionError:
        compra, venta = 0, 0

    return int(compra), int(venta)


def alberdi():
    try:
        soup = BeautifulSoup(
            requests.get('http://www.cambiosalberdi.com/', timeout=8).text, "html.parser")
        compra = soup.find_all(
            class_="span2 pagination-right")[0].string.replace('.', '')
        venta = soup.find_all(
            class_="span2 pagination-right")[1].string.replace('.', '')
    except requests.ConnectionError:
        compra, venta = 0, 0
    return int(compra), int(venta)


def bcp():
    try:
        soup = BeautifulSoup(
            requests.get('https://www.bcp.gov.py/webapps/web/cotizacion/monedas', timeout=8, 
                headers={'user-agent': 'Mozilla/5.0'}).text, "html.parser")
        ref = soup.select('#cotizacion-interbancaria > tbody > tr > td:nth-of-type(4)')[0].get_text()
        ref = ref.replace('.','').replace(',','.')
        soup = BeautifulSoup(
            requests.get('https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante', timeout=8, 
                headers={'user-agent': 'Mozilla/5.0'}).text, "html.parser")
        compra_array = soup.find(class_="table table-striped table-bordered table-condensed").select('tr > td:nth-of-type(4)')
        venta_array = soup.find(class_="table table-striped table-bordered table-condensed").select('tr > td:nth-of-type(5)')
        posicion = len(compra_array) - 1
        compra = compra_array[posicion].get_text().replace('.','').replace(',','.')
        venta = venta_array[posicion].get_text().replace('.','').replace(',','.')
    except requests.ConnectionError:
        compra, venta, ref = 0,0,0

    return Decimal(compra), Decimal(venta), Decimal(ref)
    


def create_json():
    mcompra, mventa = maxi()
    ccompra, cventa = chaco()
    acompra, aventa = alberdi()
    bcpcompra,bcpventa,bcpref = bcp()
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
        },
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return json.dumps(respjson, indent=4, sort_keys=True, separators=(',', ': '), default=decimal_default)


def get_output():
    with open('/tmp/dolar.json', 'r') as f:
        response = f.read()
    return response


def write_output():
    response = create_json()
    with open('/tmp/dolar.json', 'w') as f:
        f.write(response)

write_output()
