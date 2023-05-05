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
import markdown
import os
import boto3
import uuid
from datetime import datetime
import logging

from urllib import request as urllib_request, parse
import json

ENV_NAME = os.getenv("COPILOT_ENVIRONMENT_NAME")
LOGGING_LEVEL = logging.INFO if ENV_NAME == "production" else logging.DEBUG
DEBUG_MODE = False if ENV_NAME == "production" else True
logging.basicConfig(level=LOGGING_LEVEL)

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb')

def save_data(markdown, html):
    try:
        table = dynamodb.Table(
            os.getenv("MARKDOWNTABLE_NAME")
            )
        id = str(uuid.uuid4())
        table.update_item(
            Key={'ID': id},
            UpdateExpression="set message_markdown=:markdown, message_html=:html, request_date=:sts",
            ExpressionAttributeValues={
                ':markdown': markdown,
                ':html': html,
                ':sts': datetime.now().strftime("%m-%d-%Y %H:%M:%S")
            })
        return True
    except Exception:
        logging.exception("Error on saving data into DynamoDB", exc_info=True)
        return False


@app.route('/health', methods=['GET'])
def healthcheck():
    data = {"status": "ok"}
    return jsonify(data), 200

def call_svc_api_text(input_markdown):
    URL = "http://svc-api-text.staging.module1.internal/internal-api/text"
    internal_payload = {"text": input_markdown}
    internal_request_call = urllib_request.Request(
        URL, data=json.dumps(internal_payload).encode('utf-8'), headers={'Content-type': 'application/json'})
    internal_response = urllib_request.urlopen(internal_request_call)
    response_json = json.loads(
        internal_response.read().decode('utf-8'))
    return response_json

@app.route('/api/markdown/process', methods=['POST'])
def to_markdown():
    response_data = {}
    response_status = 500    
    try:
        logging.info("Received request: {}".format(request.json))
        if "text" not in request.json:
            response_data = {"error":"No accepted parameters"}
            response_status = 400
            return jsonify(response_data), response_status

        if "text" in request.json:
            input_markdown = request.json['text']
            html = markdown.markdown(input_markdown)
            db_status = save_data(input_markdown, html)
            if db_status:
                response_data = {"markdown": input_markdown, "html": html}
                response_status = 200
                # ADD THIS — Internal API call
                response_json = call_svc_api_text(input_markdown)
                response_data["svc-api-text"] = response_json    
                # End of change            
            else:                
                response_data = {"error": "Unable to save data to database"}
                response_status = 500
            return jsonify(response_data), response_status
    except Exception as e:
        logging.error("Error on handling request {}".format(e), exc_info=True)
        return jsonify(response_data), response_status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=DEBUG_MODE)
