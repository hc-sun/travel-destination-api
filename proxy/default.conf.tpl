server {
    listen ${LISTEN_PORT};

    location /static {
        alias /app/proxy/static;
    }

    location / {
        uwsgi_pass ${APP_HOST}:${APP_PORT};
        include /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
        proxy_set_header Host $host:$server_port;
    }
}
