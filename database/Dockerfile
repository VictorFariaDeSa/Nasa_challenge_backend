FROM postgres:16


COPY seeds/* /docker-entrypoint-initdb.d/

WORKDIR /database

CMD ["postgres"]
