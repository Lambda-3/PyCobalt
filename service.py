# -*- coding: utf-8 -*-

import datetime
import sys

from flask import Flask, jsonify, make_response, request

from pycobalt import resolve, substitute

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    return jsonify({'name': 'pyCobalt Coreference Resolver',
                    'server_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


@app.route('/resolve/text', methods=['POST'])
def resolve_text():
    data = request.get_json()
    if data is None:
        return make_response(jsonify({'message': 'No data.'}), 400)

    text = data['text']
    if not text:
        return make_response(jsonify({'message': '`text` field is mandatory.'}), 400)

    substituted = substitute(*resolve(text, ''))

    return jsonify({'text': '\n'.join(s for s in substituted)})


@app.route('/resolve/wiki', methods=['POST'])
def resolve_wiki():
    data = request.get_json()
    if data is None:
        return make_response(jsonify({'message': 'No data.'}), 400)

    text, uri = data['text'], data['uri']
    if not text or not uri:
        return make_response(jsonify({'message': '`text` and `uri` fields are mandatory.'}), 400)

    substituted = substitute(*resolve(text, uri))

    return jsonify({'text': substituted})


@app.route('/resolve/link', methods=['POST'])
def resolve_link():
    return make_response(jsonify({'message': 'Not implemented.'}), 501)


@app.errorhandler(404)
def page_not_found(_):
    return make_response(jsonify({'message': 'No interface defined for URL'}), 404)


if __name__ == "__main__":
    import os

    host = os.environ['PYCOBALT_HOST'] if 'PYCOBALT_HOST' in os.environ else '0.0.0.0'
    port = int(os.environ['PYCOBALT_PORT']) if 'PYCOBALT_PORT' in os.environ else 5128
    print("Trying to start server at '{}':'{}'".format(host, port))

    app.run(host=host, port=port, debug=False, use_reloader=False)
