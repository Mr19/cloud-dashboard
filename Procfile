web: gunicorn --pythonpath app cloud_dashboard.wsgi --log-file -

worker: python app/manage.py rqworker high
