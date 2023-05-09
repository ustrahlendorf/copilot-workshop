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


import os
import json
import boto3
import sys
import traceback
import uuid
import os
from datetime import datetime
from flask import Flask
from flask import request as _request
from flask import jsonify
import logging
import time

app = Flask(__name__)

SNS_ARN = json.loads(os.getenv('COPILOT_SNS_TOPIC_ARNS'))
AWS_REGION = os.getenv("AWS_REGION")
sns_client = boto3.client('sns', region_name=AWS_REGION)

ENV_NAME = os.getenv("COPILOT_ENVIRONMENT_NAME")
LOGGING_LEVEL = logging.INFO if ENV_NAME == "production" else logging.DEBUG
DEBUG_MODE = False if ENV_NAME == "production" else True
logging.basicConfig(level=LOGGING_LEVEL)



@app.route('/health', methods=['GET'])
def healthcheck():
    data = {"status": "ok"}
    return jsonify(data), 200


@app.route('/api/pub', methods=['POST'])
def process():
    req = _request.get_json()
    logging.info(req)
    try:
        if "text" not in req:
            return jsonify({"error": "Parameters missing"}), 422

        if not req["text"]:
            return jsonify({"error": "Parameters missing"}), 422

        request_id = str(uuid.uuid4())
        resp_sns = sns_client.publish(
            TopicArn=SNS_ARN["<CHANGE_THIS_TO_TOPIC_NAME>"],
            Message=json.dumps(
                {"payload": {"request_ID": request_id, "text": req["text"]}}))
        logging.info(resp_sns)
        return jsonify({"request_ID": request_id}), 200

    except:
        logging.error("Error on processing request", exc_info=True)
        return jsonify({"error": "error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
