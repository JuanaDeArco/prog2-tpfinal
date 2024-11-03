FROM python:3.13-alpine

LABEL maintainer="Ivana"
LABEL description="Docker para levantar la API"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=worker:worker . .

USER worker
ENTRYPOINT [ "python" ]
CMD ["App.py"]

