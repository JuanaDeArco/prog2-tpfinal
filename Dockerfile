FROM python:3.13-alpine

#Buildeo usando estos argumentos
ARG PORT=8080
ARG DATABASE_URL
ARG SECURITY_PASSWORD_SALT
ARG JWT_SECRET_KEY
ARG SECRET_KEY
ARG USER_SECRET_KEY

#...y los hago variable de entorno
ENV PORT=${PORT}
ENV DATABASE_URL=${DATABASE_URL}
ENV SECRET_KEY=${SECRET_KEY}
ENV SECURITY_PASSWORD_SALT=${SECURITY_PASSWORD_SALT}
ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}
ENV USER_SECRET_KEY=${USER_SECRET_KEY}

LABEL maintainer="Ivana"
LABEL description="Docker para levantar la API"

USER root
RUN adduser -D worker
WORKDIR /app
COPY ./app/requirements.txt ./
RUN wc -l requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=worker:worker ./app ./app
COPY --chown=worker:worker ./merendar.py .
COPY --chown=worker:worker ./config.py .

USER worker
ENTRYPOINT [ "python" ]
CMD ["merendar.py"]

