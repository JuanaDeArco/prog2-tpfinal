FROM python:3.13-alpine
ARG PORT=8080
ENV PORT=${PORT}

LABEL maintainer="Ivana"
LABEL description="Docker para levantar la API"
USER root
RUN adduser -D worker
WORKDIR /app
COPY ./jwtlog/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=worker:worker . .


USER worker
ENTRYPOINT [ "python" ]
CMD ["App.py"]

