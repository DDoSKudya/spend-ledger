FROM nginx:alpine

RUN apk upgrade --no-cache \
    && rm -f /etc/nginx/conf.d/default.conf

COPY nginx/conf.d/http-server.conf /etc/nginx/conf.d/http-server.conf
COPY docker/nginx-entrypoint.sh /docker-entrypoint.d/40-enable-ssl.sh
RUN chmod +x /docker-entrypoint.d/40-enable-ssl.sh
