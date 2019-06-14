#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import requests
import urllib3

from decimal import Decimal
from bs4 import BeautifulSoup
from datetime import datetime

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
            requests.get(
                'http://www.cambioschaco.com.py/api/branch_office/1/exchange', timeout=10).text)
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
        url = "http://cambiosalberdi.com/ws/getCotizaciones.json"
        soup = requests.get(url, timeout=10).json()
        compra = soup['asuncion'][0]['compra'].replace('.', '')
        venta = soup['asuncion'][0]['venta'].replace('.', '')
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
            requests.get(
                'https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante', timeout=10,
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
        jsonResult = requests.get(
            "https://seguro.interfisa.com.py/rest/cotizaciones", timeout=10).json()
        cotizaciones = jsonResult['operacionResponse'][
            'cotizaciones']['monedaCot']
        for coti in cotizaciones:
            for k, v in coti.items():
                if v == "DOLARES AMERICANOS":  # estamos en el dict de Dolares
                    compra = coti['compra']
                    venta = coti['venta']
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


def eurocambio():
    try:
        url = "https://eurocambios.com.py/v2/sgi/utilsDto.php"
        data = {'param': 'getCotizacionesbySucursal', 'sucursal': '1'}
        result = requests.post(url, data, timeout=10).json()
        compra = result[0]['compra']
        venta = result[0]['venta']
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def myd():
    try:
        soup = BeautifulSoup(
            requests.get('https://www.mydcambios.com.py/', timeout=10).text, "html.parser")
        compra = soup.select(
            'div.cambios-banner-text.scrollbox > ul:nth-of-type(2) > li:nth-of-type(2) ')[0].text
        venta = soup.select(
            'div.cambios-banner-text.scrollbox > ul:nth-of-type(2) > li:nth-of-type(3) ')[0].text
    except requests.ConnectionError:
        compra, venta = 0, 0
    except:
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


# def familiar():  # Comentado porque el servidor bloquea las peticiones
#     try:
#         soup = BeautifulSoup(
#             requests.get('https://www.familiar.com.py/', timeout=10).text, "html.parser")
#         compra = soup.select(
#             'hgroup:nth-of-type(1) > div:nth-of-type(2) > p:nth-of-type(2)')[0].get_text().replace('.', '')
#         venta = soup.select(
#             'hgroup:nth-of-type(1) > div:nth-of-type(3) > p:nth-of-type(2)')[0].get_text().replace('.', '')
#     except requests.ConnectionError:
#         compra, venta = 0, 0
#     except:
#         compra, venta = 0, 0

#     return Decimal(compra), Decimal(venta)


def create_json():
    mcompra, mventa = maxi()
    ccompra, cventa = chaco()
    acompra, aventa = alberdi()
    bcpcompra, bcpventa, bcpref = bcp()
    setcompra, setventa = setgov()
    intcompra, intventa = interfisa()
    ambcompra, ambventa = amambay()
    eccompra, ecventa = eurocambio()
    mydcompra, mydventa = myd()
    # famicompra, famiventa = familiar()
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
            },
            'eurocambios' : {
                'compra' : eccompra,
                'venta' : ecventa
            }
            # 'familiar': {
            #     'compra': famicompra,
            #     'venta': famiventa
            # }
        },
        "updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return json.dumps(
        respjson, indent=4, sort_keys=True, separators=(',', ': '), default=decimal_default)


def get_output():
    with open('dolar.json', 'r') as f:
        response = f.read()
    return response


def write_output():
    response = create_json()
    with open('dolar.json', 'w') as f:
        f.write(response)


write_output()
