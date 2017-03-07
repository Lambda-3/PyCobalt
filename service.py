# -*- coding: utf-8 -*-

import datetime

from flask import Flask, jsonify, make_response, request

from Resolver import Resolver

application = Flask(__name__)


@application.route('/', methods=['GET'])
def hello():
    return jsonify({'name': 'Text Coreference Resolver',
                    'server_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


@application.route('/resolve/wiki', methods=['POST'])
def resolve_wiki():
    data = request.get_json()
    if data is None:
        return make_response(jsonify({'message': 'No data.'}), 400)

    text, uri = data['text'], data['uri']
    if not text or not uri:
        return make_response(jsonify({'message': '`text` and `uri` fields are mandatory.'}), 400)

    substitutions = Resolver.resolve(text, uri)
    substituted = Resolver.substitute_in_text(text, substitutions)

    return jsonify({'text': substituted})


@application.route('/resolve/text', methods=['POST'])
def resolve_text():
    data = request.get_json()
    if data is None:
        return make_response(jsonify({'message': 'No data.'}), 400)

    text = data['text']
    if not text:
        return make_response(jsonify({'message': '`text` field is mandatory.'}), 400)

    substitutions = Resolver.resolve(text, '')
    substituted = Resolver.substitute_in_text(text, substitutions)

    return jsonify({'text': substituted})


@application.route('/resolve/link', methods=['POST'])
def resolve_link():
    return make_response(jsonify({'message': 'Not implemented.'}), 501)


@application.errorhandler(404)
def page_not_found(_):
    return make_response(jsonify({'message': 'No interface defined for URL'}), 404)


if __name__ == "__main__":
    application.run(port=5128, debug=False, use_reloader=False, host='0.0.0.0')
