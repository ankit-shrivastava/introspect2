#!/usr/bin/python
import os
import logging
import json
from flask import Flask

from log import initialize_logging
initialize_logging()

if True:
    import employees
logger = logging.getLogger(__name__)


ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__,
            static_url_path=os.path.join("/employees", 'static', "public"),
            static_folder=os.path.join(ROOT, 'build'),
            template_folder=os.path.join(ROOT, 'build'))

app.secret_key = "dd97de49cbd18a6a3dfa"
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True


# Route to define the health of the server.
# This route doesn't required to be authenticated.
@app.route('/employees/status')
def app_status():
    return json.dumps({'Status': "Healthy"}), 200


@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = 0
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


for service in [employees]:
    logger.info(f'Registering routes for service')
    service.register(app, "employees")


if __name__ == '__main__':
    run_param = {
        "debug": True,
        "port": 5000,
        "host": "0.0.0.0"
    }
    https = os.environ.get(
        'HTTP_SCHEME') if 'HTTP_SCHEME' in os.environ else None

    if https in ["True"]:
        run_param["ssl_context"] = "adhoc"
    app.run(**run_param)
