
from flask import Flask, request, jsonify, session
import markdown
import os
import boto3
import uuid
from datetime import datetime
import logging
import time
from urllib import request as urllib_request, parse
import json
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = "module6-observability"
dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-1")

ENV_NAME = os.getenv("COPILOT_ENVIRONMENT_NAME")
LOGGING_LEVEL = logging.INFO if ENV_NAME == "production" else logging.INFO
DEBUG_MODE = False if ENV_NAME == "production" else True
logging.basicConfig(level=LOGGING_LEVEL)

def save_data(markdown, html):
    try:
        logging.info('Started a saving to DB')
        table = dynamodb.Table(
            os.getenv("MARKDOWNTABLE_NAME"))
        id = uuid.uuid4()
        table.update_item(
            Key={'ID': int(id)},
            UpdateExpression="set message_markdown=:markdown, message_html=:html, request_date=:sts",
            ExpressionAttributeValues={
                ':markdown': markdown,
                ':html': html,
                ':sts': datetime.now().strftime("%m-%d-%Y %H:%M:%S")
            })
        return True
    except Exception:
        logging.exception("Error on saving data into DynamoDB")
        return False

@app.route('/health', methods=['GET'])
def healthcheck2():
    data = {"status": "ok"}
    return jsonify(data), 200


@app.route('/api/observability/process', methods=['POST'])
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
            else:                
                response_data = {"error": "Unable to save data to database"}
                response_status = 500
            return jsonify(response_data), response_status
    except Exception as e:
        logging.error("Error on handling request {}".format(e), exc_info=True)
        return jsonify(response_data), response_status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=DEBUG_MODE)
