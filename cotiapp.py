# -*- encoding: utf-8 -*-
import json
from datetime import datetime
from flask import Flask, Response, render_template,send_from_directory
from flask.ext.cors import CORS

from coti import create_json, write_output

app = Flask(__name__, static_url_path='')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/api/1.0/")
def api_root():
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
