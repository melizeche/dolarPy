#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import cloudscraper
import json
import requests
import traceback
import urllib3

from decimal import Decimal
from bs4 import BeautifulSoup
from datetime import datetime
from sys import version_info

import db

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

# Hacky and horrible solution to support different versions of Python and bs4
if version_info.major == 3 and version_info.minor >= 10:
    # In Python 3.10 collections.Callable was moved to collections.abc.Callable
    import collections
    collections.Callable = collections.abc.Callable

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def format_decimal(number):
    return str(number).replace(".", "").replace(",", ".")


def chaco():
    try:
        soup = json.loads(
            requests.get(
                "http://www.cambioschaco.com.py/api/branch_office/1/exchange",
                timeout=10,
            ).text
        )
        compra = soup["items"][0]["purchasePrice"]
        venta = soup["items"][0]["salePrice"]
    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def maxi():
    today = datetime.today().strftime("%d%m%Y")
    url = "https://www.maxicambios.com.py/"
    try:
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

    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def alberdi():
    try:
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

    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

    try:
        return Decimal(compra), Decimal(venta)
    except:
        return 0, 0


def bcp():
    try:
        scraper = cloudscraper.create_scraper()
        url_ref = "https://www.bcp.gov.py/webapps/web/cotizacion/monedas"
        url_fluct = (
            "https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante"
        )

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1',
            'Priority': 'u=0, i',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'trailers',
        }
        # Referencial diario
        response = scraper.get(url_ref, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        ref = soup.select("#cotizacion-interbancaria > tbody > tr > td:nth-of-type(4)")[
            0
        ].get_text()
        ref = ref.replace(".", "").replace(",", ".")

        # referencial fluctuante
        response = scraper.get(url_fluct, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
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
            
    except requests.ConnectionError:
        compra, venta, ref = 0, 0, 0
    except:
        compra, venta, ref = 0, 0, 0

    return Decimal(compra), Decimal(venta), Decimal(ref)


def setgov():
    try:
        soup = BeautifulSoup(
            requests.get(
                "https://www.dnit.gov.py/en/web/portal-institucional/cotizaciones",
                timeout=10,
                headers={"user-agent": "Mozilla/5.0"},
                verify=False,
            ).text,
            "html.parser",
        )

        table = soup.select("table")[0]

        last_row = table.select("tbody > tr")[-1]
        compra = last_row.select("td")[1].text.replace(".", "").replace(",", ".").strip()
        venta = last_row.select("td")[2].text.replace(".", "").replace(",", ".").strip()
        
    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

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


def eurocambio():
    try:
        url = "https://eurocambios.com.py/v2/sgi/utilsDto.php"
        data = {"param": "getCotizacionesbySucursal", "sucursal": "1"}
        result = requests.post(url, data, timeout=10).json()
        compra = result[0]["compra"]
        venta = result[0]["venta"]
    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def myd():
    try:
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
    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def bonanza():
    url = "https://bonanzacambios.com.py/"
    try:
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

    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def familiar():
    try:
        soup = BeautifulSoup(requests.get("https://www.familiar.com.py/", timeout=10).text, 'html.parser')

        compra = soup.findAll(class_='content-item flex-between horizontal-between')[2].findAll(class_='text-m')[1].get_text()
        venta = soup.findAll(class_='content-item flex-between horizontal-between')[3].findAll(class_='text-m')[1].get_text()

    except requests.ConnectionError as e:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def lamoneda():
    try:
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

        compra = tr_dolar.find_all('td')[2].text.replace(",", "").strip()
        venta = tr_dolar.find_all('td')[3].text.replace(",", "").strip()
    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)

def bbva():
    try:
        soup = requests.get(
            "https://www.bancognb.com.py/public/currency_quotations", timeout=10
        ).json()
        compra = soup["exchangeRates"][0]["cashBuyPrice"]
        venta = soup["exchangeRates"][0]["cashSellPrice"]
    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

    return Decimal(compra), Decimal(venta)


def mundial():
    soup = None
    try:
        soup = BeautifulSoup(
            requests.get('http://www.mundialcambios.com.py/?branch=6',
                         timeout=20,
                         headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}).text,
            "html.parser")
        compra = format_decimal(soup.select('td')[1].get_text())
        venta = format_decimal(soup.select('td')[2].get_text())
    except requests.ConnectionError:
        compra, venta = 0, 0
    except BaseException as e:
        print("error:", e)
        print(traceback.format_exc())
        compra, venta = 0, 0

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
    famicompra, famiventa = familiar()
    wcompra, wventa = mundial()
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
            "familiar": {"compra": famicompra, "venta": famiventa},
            "gnbfusion": {"compra": bbvacompra, "venta": bbvaventa},
            "mundialcambios": {"compra": wcompra, "venta": wventa},
            "bonanza": {
                "compra": bonanzacompra,
                "venta": bonanzaventa,
            },
            "lamoneda": {
                "compra": lamonedacompra,
                "venta": lamonedaventa,
            },
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

    #If need keep data to DB (sqlite)
    #db.add(response)
    
    with open("dolar.json", "w") as f:
        f.write(response)


write_output()