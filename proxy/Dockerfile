FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="hcsun"

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9090

USER root

RUN mkdir -p /app/proxy/static && \
    chmod 755 /app/proxy/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

VOLUME /app/proxy/static

USER nginx-user

CMD ["/run.sh"]
