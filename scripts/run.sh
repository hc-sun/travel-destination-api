#!/bin/sh

# Run the deployment script

set -e

python mange.py wait_for_db
ptyhon mange.py collectstatic --noinput
python mange.py migrate

uwsgi --socket :8000 --workers 4 --master --enable-threads --module app.wsgi
