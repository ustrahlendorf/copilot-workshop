# MIT No Attribution

# Copyright 2022 AWS

# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from flask import Flask, request, jsonify
import os
from datetime import datetime
import logging


ENV_NAME = os.getenv("COPILOT_ENVIRONMENT_NAME")
LOGGING_LEVEL = logging.INFO if ENV_NAME == "production" else logging.DEBUG
DEBUG_MODE = False if ENV_NAME == "production" else True
logging.basicConfig(level=LOGGING_LEVEL)


app = Flask(__name__)


@app.route('/health', methods=['GET'])
def healthcheck():
    data = {"status": "ok"}
    return jsonify(data), 200


@app.route('/internal-api/text', methods=['POST'])
def count():
    response_data = {}
    response_status = 500
    try:
        if "text" in request.json:
            input_text = request.json['text']
            count_word = 0
            count_char = 0
            # Get total word and characters for given input
            for word in input_text.split():
                count_word += 1
                count_char += len(word)

            response_data = {"count_word": count_word,
                             "count_characters": count_char}
            response_status = 200
    except Exception as e:
        logging.error("Error on processing {}".format(e), exc_info=True)
    return jsonify(response_data), response_status


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=DEBUG_MODE)
