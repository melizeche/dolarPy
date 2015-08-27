#!/usr/bin/python
import json
import urllib2

from bs4 import BeautifulSoup
from datetime import datetime


def chaco():
    try:
        soup = BeautifulSoup(
            urllib2.urlopen('http://www.cambioschaco.com.py/php/imprimir_.php').read(), "html.parser")
        compra = soup.find_all('tr')[3].contents[5].string[:5].replace('.', '')
        venta = soup.find_all('tr')[3].contents[7].string[:5].replace('.', '')
    except urllib2.URLError:
        compra, venta = 0, 0

    return int(compra), int(venta)


def maxi():
    try:
        soup = BeautifulSoup(
            urllib2.urlopen('http://www.maxicambios.com.py/').read(), "html.parser")
        compra = soup.find_all(class_='lineas1')[0].contents[
            7].string.replace('.', '')
        venta = soup.find_all(class_='lineas1')[0].contents[
            5].string.replace('.', '')
    except urllib2.URLError:
        compra, venta = 0, 0

    return int(compra), int(venta)


def alberdi():
    try:
        soup = BeautifulSoup(
            urllib2.urlopen('http://www.cambiosalberdi.com/').read(), "html.parser")
        compra = soup.find_all(
            class_="span2 pagination-right")[0].string.replace('.', '')
        venta = soup.find_all(
            class_="span2 pagination-right")[1].string.replace('.', '')
    except urllib2.URLError:
        compra, venta = 0, 0
    return int(compra), int(venta)


def create_json():
    mcompra, mventa = maxi()
    ccompra, cventa = chaco()
    acompra, aventa = alberdi()
    respjson = {
        'dolarpy': {
            'maxicambios': {
                'compra': mcompra,
                'venta': mventa
            },
            'cambioschaco': {
                'compra': ccompra,
                'venta': cventa
            },
            'cambiosalberdi': {
                'compra': acompra,
                'venta': aventa
            }
        },
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return json.dumps(respjson, sort_keys=True, indent=4, separators=(',', ': '))


def get_output():
    with open('/tmp/dolar.json', 'r') as f:
        response = f.read()
    return response


def write_output():
    response = create_json()
    with open('/tmp/dolar.json', 'w') as f:
        f.write(response)

write_output()
