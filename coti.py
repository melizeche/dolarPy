#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import traceback
from datetime import datetime, date
from decimal import Decimal
from websocket import create_connection


import requests
from bs4 import BeautifulSoup
from bson import ObjectId
from pymongo import MongoClient

errores = {}
MONGO_SERVER_IP = "127.0.0.1"
MONGO_SERVER_PORT = 101010
client = MongoClient(host=MONGO_SERVER_IP, port=101010, connect=False)
db = client.local


def log_error(who, error, trace=None, soup=None):
    errores[who] = {}
    errores[who]['error'] = str(error.message)
    if trace:
        errores[who]['traceback'] = str(trace)
    if soup:
        errores[who]['soup'] = str(soup)


def json_default(obj):
    if isinstance(obj, float):
        return Decimal(obj)
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError


def serializar(result, formato=None):
    if formato:
        return result
    else:
        return json.dumps(result, indent=4, sort_keys=True,
                          separators=(',', ': '), default=json_default)


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
    try:
        soup = BeautifulSoup(
            requests.get('http://www.maxicambios.com.py/', timeout=10).text, "html.parser")
        compra = soup.find_all(class_='lineas1')[0].contents[
            7].string.replace('.', '')
        venta = soup.find_all(class_='lineas1')[0].contents[
            5].string.replace('.', '')
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
                         headers={'user-agent': 'Mozilla/5.0'}).text, "html.parser")
        ref = soup.select(
            '#cotizacion-interbancaria > tbody > tr > td:nth-of-type(4)')[0].get_text()
        ref = ref.replace('.', '').replace(',', '.')
        soup = BeautifulSoup(
            requests.get('https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante', timeout=10,
                         headers={'user-agent': 'Mozilla/5.0'}).text, "html.parser")
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


def get_exchange_dict():
    mcompra, mventa = maxi()
    ccompra, cventa = chaco()
    acompra, aventa = alberdi()
    bcpcompra, bcpventa, bcpref = bcp()
    setcompra, setventa = setgov()
    intcompra, intventa = interfisa()
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
            }
        },
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return json.dumps(respjson, indent=4, sort_keys=True, separators=(',', ': '), default=decimal_default)


def send_mongo(data_to_send):
    """
    Takes a dictionary and sends it to the MongoDB setted up at the beggining
    of the file.
    :param data_to_send: Dict to send.
    """
    # db is the database, cotizacion is the collection.
    db.cotizacion.insert_one(data_to_send)


def receive_mongo(values={}, formato=None):
    """
    Searchs in the db the most recent entries and returns a dict or a json with
    the data received
    :param values: parameters that define what to get from the database
    find an exchangerate, if not provided it returns the most recent entry with
    every exchange rate
    :param formato: To serialize or not. Defaults to serialize to json.
    :return: Json string or python dict
    """
    date_parameter = values.get('updated', datetime.now())
    exchage_name = values.get('usdpyg')
    if isinstance(date_parameter, (str, unicode)):
        if len(date_parameter) > 10:
            date_parameter = datetime.strptime(date_parameter,
                                               '%Y-%m-%d %H:%M:%S')
        else:
            date_parameter = datetime.strptime(date_parameter, '%Y-%m-%d')
    result = []
    agg = db.cotizacion.aggregate([{"$match": {"updated": {"$lt": date_parameter}}},{"$sort": {"updated": -1}}])
    for each in agg:
        # Rompe el loop despues del primer elemento encontrado en el cursor.
        result = each
        break

    if exchage_name:
        temp = dict()
        temp['dolarpy'] = dict()
        temp['dolarpy'][exchage_name] = result['dolarpy'][exchage_name]
        temp['updated'] = result['updated']
        return serializar(temp, formato)
    else:
        return serializar(result, formato)


def create_json():
    """
    Creates a dictionary and then sends it to the database.
    :return: Json from the dictionary.
    """
    exchange = get_exchange_dict()
    send_mongo(exchange)
    return serializar(exchange)


def get_output():
    with open('dolar.json', 'r') as f:
        response = f.read()
    return response


def write_output():
    response = create_json()
    errores_json = json.dumps(errores)

    with open('dolar.json', 'w') as f:
        f.write(response)

    with open('error.log', 'w') as f:
        f.write(errores_json)


write_output()
