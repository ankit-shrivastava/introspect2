import os
import logging
import json
from flask import request
import requests


ROOT = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

DBMS_URI = os.environ.get(
    'DBMS_URI') if 'DBMS_URI' in os.environ else "http://localhost:5000/dbms"
DEPT_URI = os.environ.get(
    'DEPT_URI') if 'DEPT_URI' in os.environ else "http://localhost:5000/departments"


def add_employee():
    logger.info(f'Add employee API call')
    data = request.get_json()

    data_error = False
    if not data:
        msg = "Failed to get the new employee id in API call"
        data_error = True
    else:
        data_error = True
        if 'id' not in data:
            msg = "Failed to get the new employee id in API call"
        elif 'name' not in data:
            msg = "Failed to get the new employee name in API call"
        elif 'dept_id' not in data:
            msg = "Failed to get the new employee department id in API call"
        elif 'package' not in data:
            msg = "Failed to get the new employee package in API call"
        elif 'job_name' not in data:
            msg = "Failed to get the new employee job_name in API call"
        else:
            data_error = False

    if data_error:
        logger.error(msg)
        return json.dumps(msg), 500

    id = data['id']
    name = data['name']
    dept_id = data['dept_id']
    job_name = data['job_name']
    package = data['package']

    # Validate the new employee id
    query = (
        f"SELECT ID, NAME FROM EMPLOYEE WHERE ID like '{id}';"
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
        emp_name = result["results"]["NAME"]
        msg = f"Employee ID = '{id}' already present as name = '{emp_name}'"
        logger.error(msg)
        return json.dumps(msg), 400

    # Validate dept id
    result = requests.get(f"{DEPT_URI}/department/search?id={dept_id}")
    if not result or result.status_code != 200:
        msg = "Failed to establish connection with database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    result = json.loads(result.text)
    logger.info(result)
    if not result:
        msg = f"Invalid department id = '{dept_id}'"
        logger.error(msg)
        return json.dumps(msg), 400

    # all validation done
    query = (
        f"INSERT INTO EMPLOYEE (ID, NAME, JOB_NAME, DEPT_ID, PACKAGE)"
        f" VALUES ({id}, '{name}', '{job_name}', {dept_id}, {package});"
    )
    query = {'query': query}
    result = requests.post(f"{DBMS_URI}/execute/query", json=query)
    if not result or result.status_code != 200:
        msg = "Failed to stablish connection with database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    msg = f"Employee added as ID = '{id}' name '{name}' under department '{dept_id}'"
    return json.dumps({'Success': msg}), 200


def search_employee():
    logger.info(f'Search employee API')

    id = None
    name = None
    dept_id = None
    if request.args:
        if 'id' in request.args and request.args["id"]:
            id = request.args["id"]
        if 'name' in request.args and request.args["name"]:
            name = request.args["name"]
        if 'dept_id' in request.args and request.args["dept_id"]:
            dept_id = request.args["dept_id"]

    if not id and not name and not dept_id:
        msg = "Failed to get the employee parameter for search"
        logger.error(msg)
        return json.dumps(msg), 500

    query = (
        f"SELECT ID, NAME, JOB_NAME, DEPT_ID FROM EMPLOYEE WHERE"
    )
    if id:
        query = f"{query} ID like '{id}'"

    if name:
        if id:
            query = f"{query} OR"
        query = f"{query} NAME like '%{name}%'"

    if dept_id:
        if id or name:
            query = f"{query} OR"
        query = f"{query} DEPT_ID like '{dept_id}';"
    query = {'query': query}

    result = requests.post(f"{DBMS_URI}/execute/query", json=query)
    if not result or result.status_code != 200:
        msg = "Failed to establish connection with database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    result = json.loads(result.text)
    if result or not 'results' in result:
        msg = "Failed to get results from database microservice"
        logger.error(msg)
        return json.dumps(msg), 500

    logger.info(result["results"])
    return json.dumps(result["results"]), 200


def fetch_employees():
    logger.info(f'Fetch all employees')

    query = (
        f"SELECT ID, NAME, JOB_NAME, DEPT_ID FROM EMPLOYEE;"
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
    app.add_url_rule(rule=f'/{context_name}/employee/add',
                     endpoint='add',
                     methods=['POST'],
                     view_func=add_employee)
    # app.add_url_rule(rule=f'/{context_name}/department/search',
    #                  endpoint='search',
    #                  methods=['GET'],
    #                  view_func=search_department)
    app.add_url_rule(rule=f'/{context_name}/employee/all',
                     endpoint='fetch',
                     methods=['GET'],
                     view_func=fetch_employees)
