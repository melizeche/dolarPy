# -*- encoding: utf-8 -*-
"""Trimmed-down copies of the markup/JSON each source returns.

Only the parts the scrapers actually select are kept, plus enough noise
(extra rows, extra tables) to make sure the selectors really do pick the
dollar row and not just "the first thing on the page".
"""

CHACO_JSON = {
    "items": [
        {"isoCode": "USD", "purchasePrice": 7180, "salePrice": 7280},
        {"isoCode": "EUR", "purchasePrice": 7800, "salePrice": 7950},
    ]
}

MAXI_HTML = """
<html><body>
  <table><tbody><tr><td>decoy</td><td>1</td><td>2</td></tr></tbody></table>
  <div class="fixed-plugin">
    <table>
      <thead><tr><th>Moneda</th><th>Compra</th><th>Venta</th></tr></thead>
      <tbody>
        <tr><td>Dolar</td><td>7150</td><td>7250</td></tr>
        <tr><td>Euro</td><td>7800</td><td>7950</td></tr>
      </tbody>
    </table>
  </div>
</body></html>
"""

ALBERDI_HTML = u"""
<html><body>
  <table class="table">
    <tbody>
      <tr><td>Euro</td><td>7.800</td><td>7.950</td></tr>
      <tr><td> Dólar Americano </td><td> 7.190 </td><td> 7.290 </td></tr>
      <tr><td>Real</td><td>1.300</td><td>1.400</td></tr>
    </tbody>
  </table>
</body></html>
"""

ALBERDI_HTML_NO_DOLLAR = """
<html><body>
  <table class="table">
    <tbody>
      <tr><td>Euro</td><td>7.800</td><td>7.950</td></tr>
    </tbody>
  </table>
</body></html>
"""

BCP_REFERENCIAL_HTML = """
<html><body>
  <table id="cotizacion-interbancaria">
    <tbody>
      <tr><td>USD</td><td>Dolar</td><td>x</td><td>7.222,33</td></tr>
    </tbody>
  </table>
</body></html>
"""

BCP_FLUCTUANTE_HTML = """
<html><body>
  <table class="table table-striped table-bordered table-condensed">
    <tbody>
      <tr><td>08:00</td><td>a</td><td>b</td><td>7.100,00</td><td>7.200,00</td></tr>
      <tr><td>12:00</td><td>a</td><td>b</td><td>7.150,50</td><td>7.250,50</td></tr>
    </tbody>
  </table>
</body></html>
"""

SET_HTML = """
<html><body>
  <table>
    <tbody>
      <tr><td>01/09/2025</td><td>7.100</td><td>7.200</td></tr>
      <tr><td>02/09/2025</td><td> 7.160 </td><td> 7.260 </td></tr>
    </tbody>
  </table>
  <table><tbody><tr><td>other</td><td>1</td><td>2</td></tr></tbody></table>
</body></html>
"""

EUROCAMBIO_JSON = [
    {"moneda": "DOLAR", "compra": "7170", "venta": "7270"},
    {"moneda": "EURO", "compra": "7800", "venta": "7950"},
]

MYD_HTML = """
<html><body>
  <div class="cambios-banner-text scrollbox">
    <ul><li>Moneda</li><li>Compra</li><li>Venta</li></ul>
    <ul><li>DOLAR</li><li>7140</li><li>7240</li></ul>
    <ul><li>EURO</li><li>7800</li><li>7950</li></ul>
  </div>
</body></html>
"""

BONANZA_HTML = """
<html><body>
  <div class="table-pricing style1">
    <table>
      <tbody>
        <tr>
          <td class="pais">USD</td>
          <td class="moneda">7.130</td>
          <td class="moneda">7.230</td>
        </tr>
      </tbody>
    </table>
  </div>
</body></html>
"""

FAMILIAR_HTML = """
<html><body>
  <div class="content-item flex-between horizontal-between">
    <span class="text-m">Euro</span><span class="text-m">7800</span>
  </div>
  <div class="content-item flex-between horizontal-between">
    <span class="text-m">Euro venta</span><span class="text-m">7950</span>
  </div>
  <div class="content-item flex-between horizontal-between">
    <span class="text-m">Dolar compra</span><span class="text-m">7110</span>
  </div>
  <div class="content-item flex-between horizontal-between">
    <span class="text-m">Dolar venta</span><span class="text-m">7210</span>
  </div>
</body></html>
"""

LAMONEDA_HTML = """
<html><body>
  <table>
    <tbody>
      <tr><td>DOLAR</td><td> 7.120 </td><td> 7.220 </td></tr>
      <tr><td>EURO</td><td>7.800</td><td>7.950</td></tr>
    </tbody>
  </table>
</body></html>
"""

BBVA_JSON = {
    "exchangeRates": [
        {"currency": "USD", "cashBuyPrice": 7160, "cashSellPrice": 7260},
        {"currency": "EUR", "cashBuyPrice": 7800, "cashSellPrice": 7950},
    ]
}

MUNDIAL_HTML = """
<html><body>
  <table>
    <tbody>
      <tr><td>DOLAR</td><td>7.170</td><td>7.270</td></tr>
    </tbody>
  </table>
</body></html>
"""
