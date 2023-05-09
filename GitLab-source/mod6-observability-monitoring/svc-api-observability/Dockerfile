FROM python:3.8.3-slim-buster
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY app.py ./
EXPOSE 9090

# Automatic Instrumentation
RUN opentelemetry-bootstrap -a install
ENV OTEL_PROPAGATORS=xray
ENV OTEL_PYTHON_ID_GENERATOR=xray
ENV OTEL_SERVICE_NAME="svc-api-observability"
CMD ["opentelemetry-instrument", "python3", "app.py"]
