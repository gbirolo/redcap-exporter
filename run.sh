#!/bin/bash

. .venv/bin/activate
#flask --app redcap_exporter run
#https://compbiomed.hpc4ai.unito.it/redcap-exporter/
gunicorn --workers 4 --bind '127.0.0.1:10060' --capture-output --log-file=./gunicorn.log 'redcap_exporter:create_app()'
