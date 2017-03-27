# -*- encoding: utf-8 -*-
from flask import Flask, Response, render_template, request
from flask_cors import CORS

from coti import create_json, write_output, receive_mongo

app = Flask(__name__, static_url_path='')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/1.0/", methods=['POST', 'GET'])
def api_root_1():
    response = ""
    try:
        with open('dolar.json', 'r') as f:
            response = f.read()
    except IOError:
        response = create_json()
        write_output()
    return Response(response=response, status=200, mimetype='application/json')


@app.route("/api/2.0/", methods=['POST', 'GET'])
def api_mongo():
    response = ""
    dictionary = request.json
    try:
        if request.json:
            response = receive_mongo(values=dictionary)
        else:
            response = receive_mongo(values={})
    except IOError:
        response = create_json()
        write_output()
    return Response(response=response, status=200, mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True)
