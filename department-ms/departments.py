import os
import logging
import json
from flask import request
import requests


ROOT = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

DBMS_URI = os.environ.get(
    'DBMS_URI') if 'DBMS_URI' in os.environ else "http://localhost:5000/dbms"


def add_department():
    logger.info(f'Add depatments call')
    data = request.get_json()

    if not data or 'id' not in data:
        msg = "Failed to get the new department id from API call"
        logger.error(msg)
        return json.dumps(msg), 500

    id = data['id']
    name = data['name']

    # Validate the new department
    query = (
        f"SELECT ID, NAME FROM DEPARTMENT WHERE ID like '{id}'"
        f" or NAME like '{name}';"
    )
    query = {'query': query}

    result = requests.post(f"{DBMS_URI}/execute/query", json=query)
    if not result or result.status_code != 200:
        msg = "Failed to establish connection with database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    result = json.loads(result.text)
    if not 'results' in result:
        msg = "Failed to get results from database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    if result["results"]:
        msg = f"Department ID = '{id}' or name = '{name}' already present"
        logger.error(msg)
        return json.dumps(msg), 400
    else:
        logger.info("Validation success, will add new depatment")
        query = (
            f"INSERT INTO DEPARTMENT (ID, NAME)"
            f" VALUES ('{id}', '{name}');"
        )
        query = {'query': query}
        result = requests.post(f"{DBMS_URI}/execute/query", json=query)
        if not result or result.status_code != 200:
            msg = "Failed to stablish connection with database microservice"
            logger.error(msg)
            return json.dumps(msg), 500

    msg = f"Department ID = '{id}' added as '{name}'"
    return json.dumps({'Success': msg}), 200


def search_department():
    logger.info(f'Search depatments API')
    id = None
    name = None
    if request.args:
        if 'id' in request.args and request.args["id"]:
            id = request.args["id"]
        if 'name' in request.args and request.args["name"]:
            name = request.args["name"]

    if not id and not name:
        msg = "Failed to get the department for search"
        logger.error(msg)
        return json.dumps(msg), 500

    query = (
        f"SELECT ID, NAME FROM DEPARTMENT WHERE ID like '{id}'"
        f" or NAME like '{name}';"
    )
    query = {'query': query}

    result = requests.post(f"{DBMS_URI}/execute/query", json=query)
    if not result or result.status_code != 200:
        msg = "Failed to establish connection with database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    result = json.loads(result.text)
    if not 'results' in result:
        msg = "Failed to get results from database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    logger.info(result["results"])
    return json.dumps(result["results"]), 200


def fetch_departments():
    logger.info(f'Fetch all depatments')

    query = (
        f"SELECT ID, NAME FROM DEPARTMENT;"
    )
    query = {'query': query}
    result = requests.post(f"{DBMS_URI}/execute/query", json=query)
    if not result or result.status_code != 200:
        msg = "Failed to establish connection with database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    result = json.loads(result.text)
    if not 'results' in result or not result["results"]:
        msg = "Failed to get results from database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    logger.info(result["results"])
    return json.dumps(result["results"]), 200


def register(app, context_name):
    logger.info(f'Registering routes for {context_name}')
    app.add_url_rule(rule=f'/{context_name}/department/add',
                     endpoint='add',
                     methods=['POST'],
                     view_func=add_department)
    app.add_url_rule(rule=f'/{context_name}/department/search',
                     endpoint='search',
                     methods=['GET'],
                     view_func=search_department)
    app.add_url_rule(rule=f'/{context_name}/department/all',
                     endpoint='fetch',
                     methods=['GET'],
                     view_func=fetch_departments)
