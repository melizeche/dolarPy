#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import json
import requests
import urllib3

from decimal import Decimal
from bs4 import BeautifulSoup
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

import argparse

parser = argparse.ArgumentParser(
                    prog='dolarPy',
                    epilog='dolarPy')

parser.add_argument('-v', '--verbose',
                    action='store_true')

args = parser.parse_args()

def verbose_print(str):
    if args.verbose:
        print(str)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def format_decimal(number):
    return str(number).replace(".", "").replace(",", ".")


def exception_handler(log, func):
    verbose_print("Error in %s : %s" % (func, log))


def handle_exceptions(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kw):
        try:
            return fn(*args, **kw)
        except Exception as e:
            exception_handler(e, fn.__name__)
            return Decimal(0), Decimal(0)
    return wrapper


@handle_exceptions
def vision():
    soup = None
    soup = BeautifulSoup(
        requests.get('https://www.visionbanco.com', timeout=10,
                     headers={'user-agent': 'Mozilla/5.0'}, verify=False).text, "html.parser")

    efectivo = soup.select('#efectivo')[0]
    compra = efectivo.select(
        'table > tr > td:nth-of-type(2) > p:nth-of-type(1)')[0].get_text().replace('.', '')
    venta = efectivo.select(
        'table > tr > td:nth-of-type(3) > p:nth-of-type(1)')[0].get_text().replace('.', '')

    return Decimal(compra), Decimal(venta)


@handle_exceptions
def chaco():
    soup = json.loads(
        requests.get(
            "http://www.cambioschaco.com.py/api/branch_office/1/exchange",
            timeout=10,
        ).text
    )
    compra = soup["items"][0]["purchasePrice"]
    venta = soup["items"][0]["salePrice"]

    return Decimal(compra), Decimal(venta)


@handle_exceptions
def maxi():
    today = datetime.today().strftime("%d%m%Y")
    url = "https://www.maxicambios.com.py/"
    soup = BeautifulSoup(
        requests.get(
            url,
            timeout=10,
            headers={"user-agent": "Mozilla/5.0"},
            verify=False,
        ).text,
        "html.parser",
    )

    tr_dolar = soup.find(
        class_="fixed-plugin").find("table").find("tbody").find("tr")

    compra = tr_dolar.find_all('td')[1].text
    venta = tr_dolar.find_all('td')[2].text

    return Decimal(compra), Decimal(venta)


@handle_exceptions
def alberdi():
    soup = BeautifulSoup(
        requests.get(
            "https://www.cambiosalberdi.com/langes/index.php#sectionCotizacion",
            timeout=10,
            headers={"user-agent": "Mozilla/5.0"},
            verify=False,
        ).text,
        "html.parser",
    )

    table = soup.find('table', class_='table')

    if table:
        rows = table.tbody.find_all('tr')

        for row in rows:
            cells = row.find_all('td')

            currency_name = cells[0].text.strip()

            if "Dólar Americano" in currency_name:
                compra = cells[1].text.strip().replace('.', '')
                venta = cells[2].text.strip().replace('.', '')
                return Decimal(compra), Decimal(venta)
            else:
                compra, venta = 0, 0

    try:
        return Decimal(compra), Decimal(venta)
    except:
        return 0, 0


@handle_exceptions
def bcp():
    soup = BeautifulSoup(
        requests.get(
            "https://www.bcp.gov.py/webapps/web/cotizacion/monedas",
            timeout=10,
            headers={"user-agent": "Mozilla/5.0"},
            verify=False,
        ).text,
        "html.parser",
    )
    ref = soup.select("#cotizacion-interbancaria > tbody > tr > td:nth-of-type(4)")[
        0
    ].get_text()
    ref = ref.replace(".", "").replace(",", ".")
    soup = BeautifulSoup(
        requests.get(
            "https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante",
            timeout=10,
            headers={"user-agent": "Mozilla/5.0"},
            verify=False,
        ).text,
        "html.parser",
    )
    compra_array = soup.find(
        class_="table table-striped table-bordered table-condensed"
    ).select("tr > td:nth-of-type(4)")
    venta_array = soup.find(
        class_="table table-striped table-bordered table-condensed"
    ).select("tr > td:nth-of-type(5)")
    posicion = len(compra_array) - 1
    compra = compra_array[posicion].get_text().replace(
        ".", "").replace(",", ".")
    venta = venta_array[posicion].get_text().replace(
        ".", "").replace(",", ".")

    return Decimal(compra), Decimal(venta), Decimal(ref)


@handle_exceptions
def setgov():
    soup = BeautifulSoup(
        requests.get(
            "https://www.set.gov.py/portal/PARAGUAY-SET",
            timeout=10,
            headers={"user-agent": "Mozilla/5.0"},
            verify=False,
        ).text,
        "html.parser",
    )
    compra = (
        soup.select("td.UICotizacion")[0].text.replace(
            "G. ", "").replace(".", "").strip()
    )
    venta = (
        soup.select("td.UICotizacion")[1].text.replace(
            "G. ", "").replace(".", "").strip()
    )

    return Decimal(compra), Decimal(venta)


# def interfisa():
#     try:
#         jsonResult = requests.get(
#             "https://seguro.interfisa.com.py/rest/cotizaciones", timeout=10
#         ).json()
#         cotizaciones = jsonResult["operacionResponse"]["cotizaciones"]["monedaCot"]
#         for coti in cotizaciones:
#             for k, v in coti.items():
#                 if v == "DOLARES AMERICANOS":  # estamos en el dict de Dolares
#                     compra = coti["compra"]
#                     venta = coti["venta"]
#     except requests.ConnectionError:
#         compra, venta = 0, 0
#     except:
#         compra, venta = 0, 0

#     return Decimal(compra), Decimal(venta)


# def amambay():
#     try:
#         soup = BeautifulSoup(
#             requests.get(
#                 "https://www.bancobasa.com.py/", timeout=10).text,
#             "html.parser",
#         )
#         compra = soup.select(".trendscontent > li:nth-of-type(1) > a > .compra")[0].text.replace(".", "") 
#         venta = soup.select(".trendscontent > li:nth-of-type(1) > a > .venta")[0].text.replace(".", "") 
#     except requests.ConnectionError:
#         compra, venta = 0, 0
#     except:
#         compra, venta = 0, 0

#     return Decimal(compra), Decimal(venta)


@handle_exceptions
def eurocambio():

    url = "https://eurocambios.com.py/v2/sgi/utilsDto.php"
    data = {"param": "getCotizacionesbySucursal", "sucursal": "1"}
    result = requests.post(url, data, timeout=10).json()
    compra = result[0]["compra"]
    venta = result[0]["venta"]

    return Decimal(compra), Decimal(venta)


@handle_exceptions
def myd():

    soup = BeautifulSoup(
        requests.get("https://www.mydcambios.com.py/", timeout=10).text,
        "html.parser",
    )
    compra = soup.select(
        "div.cambios-banner-text.scrollbox > ul:nth-of-type(2) > li:nth-of-type(2) "
    )[0].text
    venta = soup.select(
        "div.cambios-banner-text.scrollbox > ul:nth-of-type(2) > li:nth-of-type(3) "
    )[0].text

    return Decimal(compra), Decimal(venta)


@handle_exceptions
def bonanza():
    url = "https://bonanzacambios.com.py/"

    soup = BeautifulSoup(
        requests.get(
            url,
            timeout=10,
            headers={"user-agent": "Mozilla/5.0"},
            verify=False,
        ).text,
        "html.parser",
    )

    tr_dolar = soup.select(".table-pricing.style1 table tbody tr td.moneda")

    compra = tr_dolar[0].get_text().replace('.', '')
    venta = tr_dolar[1].get_text().replace('.', '')

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


@handle_exceptions
def lamoneda():

    # soup = BeautifulSoup(
    #     requests.get(
    #         "http://www.lamoneda.com.py/", timeout=10).text,
    #     "html.parser",
    # )
    # casacentral = soup.select("#cotizaciones table tr:nth-of-type(2)")[0]
    # compra = (
    #     casacentral.select("td:nth-of-type(3) > div")[0].text.replace(".", "")
    # )
    # venta = (
    #     casacentral.select("td:nth-of-type(4) > div")[0].text.replace(".", "")
    # )
    today = datetime.today().strftime("%d%m%Y")
    url = "http://www.lamoneda.com.py/"
    soup = BeautifulSoup(
        requests.get(
            url,
            timeout=10,
            headers={"user-agent": "Mozilla/5.0"},
            verify=False,
        ).text,
        "html.parser",
    )

    tr_dolar = soup.find("table").find("tbody").find("tr")

    compra = tr_dolar.find_all('td')[2].text.replace(".", "")
    venta = tr_dolar.find_all('td')[3].text.replace(".", "")

    return Decimal(compra), Decimal(venta)


@handle_exceptions
def bbva():

    soup = requests.get(
        "https://www.bancognb.com.py/public/currency_quotations", timeout=10
    ).json()
    compra = soup["exchangeRates"][0]["cashBuyPrice"]
    venta = soup["exchangeRates"][0]["cashSellPrice"]

    return Decimal(compra), Decimal(venta)


@handle_exceptions
def mundial():
    soup = None

    soup = BeautifulSoup(
        requests.get('http://www.mundialcambios.com.py/?branch=6',
                     timeout=20,
                     headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}).text,
        "html.parser")
    compra = soup.select(
        'h3.divisa')[0].get_text().replace('.', '')
    venta = soup.select(
        'h3.divisa')[1].get_text().replace('.', '')

    return Decimal(compra), Decimal(venta)


def create_json():
    mcompra, mventa = maxi()
    ccompra, cventa = chaco()
    acompra, aventa = alberdi()
    bcpcompra, bcpventa, bcpref = bcp()
    setcompra, setventa = setgov()
    # intcompra, intventa = interfisa()
    # ambcompra, ambventa = amambay()
    eccompra, ecventa = eurocambio()
    mydcompra, mydventa = myd()
    bbvacompra, bbvaventa = bbva()
    # famicompra, famiventa = familiar()
    wcompra, wventa = mundial()
    visioncompra, visionventa = vision()
    bonanzacompra, bonanzaventa = bonanza()
    lamonedacompra, lamonedaventa = lamoneda()

    respjson = {
        "dolarpy": {
            "cambiosalberdi": {"compra": acompra, "venta": aventa},
            "cambioschaco": {"compra": ccompra, "venta": cventa},
            "maxicambios": {"compra": mcompra, "venta": mventa},
            "bcp": {
                "compra": bcpcompra,
                "venta": bcpventa,
                "referencial_diario": bcpref,
            },
            "set": {"compra": setcompra, "venta": setventa},
            # "interfisa": {"compra": intcompra, "venta": intventa},
            # "amambay": {"compra": ambcompra, "venta": ambventa},
            "mydcambios": {"compra": mydcompra, "venta": mydventa},
            "eurocambios": {"compra": eccompra, "venta": ecventa},
            # 'familiar': {
            #     'compra': famicompra,
            #     'venta': famiventa
            # }
            "gnbfusion": {"compra": bbvacompra, "venta": bbvaventa},
            "mundialcambios": {"compra": wcompra, "venta": wventa},
            'vision': {
                'compra': visioncompra,
                'venta': visionventa,
            },
            'bonanza': {
                'compra': bonanzacompra,
                'venta': bonanzaventa,
            },
            'lamoneda': {
                'compra': lamonedacompra,
                'venta': lamonedaventa,
            }
        },
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return json.dumps(
        respjson,
        indent=4,
        sort_keys=True,
        separators=(",", ": "),
        default=decimal_default,
    )


def get_output():
    with open("dolar.json", "r") as f:
        response = f.read()
    return response


def write_output():
    response = create_json()
    with open("dolar.json", "w") as f:
        f.write(response)


write_output()
