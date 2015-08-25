import json
from datetime import datetime
from flask import Flask, Response

from coti import create_json, write_output
app = Flask(__name__)


@app.route("/")
def hello():
    response = ""
    try:
        with open('/tmp/dolar.json', 'r') as f:
            response = f.read()
    except IOError:
        response = create_json()
        write_output()
    return Response(response=response, status=200, mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True)
