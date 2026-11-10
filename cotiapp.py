# -*- encoding: utf-8 -*-
import json

from flask import Flask, Response, render_template, request
from flask_cors import CORS

import history
from coti import create_json, write_output

app = Flask(__name__, static_url_path='')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def json_response(payload, status=200):
    return Response(response=json.dumps(payload), status=status, mimetype='application/json')


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/1.0/")
def api_root():
    response = ""
    try:
        with open('dolar.json', 'r') as f:
            response = f.read()
    except IOError:
        response = create_json()
        write_output()
    return Response(response=response, status=200, mimetype='application/json')


@app.route("/api/1.0/history/")
def api_history():
    """How the rates moved: /api/1.0/history/?source=familiar&days=30&by=day"""
    source = request.args.get("source") or None
    by = request.args.get("by", "day")
    try:
        days = int(request.args.get("days", history.DEFAULT_DAYS))
    except ValueError:
        days = 0
    if not 1 <= days <= history.MAX_DAYS:
        return json_response(
            {"error": "days must be a whole number from 1 to %d" % history.MAX_DAYS}, 400
        )
    if by not in ("day", "run"):
        return json_response({"error": "by must be 'day' or 'run'"}, 400)
    if by == "run" and days > history.MAX_RUN_DAYS:
        # every run is ~90 points a day per source; keep the answer small
        return json_response(
            {"error": "by=run goes up to %d days" % history.MAX_RUN_DAYS}, 400
        )
    if source is not None and source not in history.sources():
        return json_response({"error": "no history for source '%s'" % source}, 404)

    return json_response({
        "days": days,
        "by": by,
        "history": history.query(source=source, days=days, by=by),
    })


if __name__ == "__main__":
    app.run(debug=True)
