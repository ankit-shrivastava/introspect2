import os
import logging
import json
import sqlite3
from flask import request

ROOT = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)

dbms_home = os.environ.get('DBMS_HOME') if 'DBMS_HOME' in os.environ else None
database = "emp"
sqlite_db_path = os.path.join(ROOT)

if dbms_home:
    if os.path.exists(dbms_home):
        sqlite_db_path = dbms_home

database_file = os.path.join(sqlite_db_path, f"{database}.db")


def create_employee_schema():
    logger.info(f'Create schema call')
    data = request.get_json()

    override = False
    if data and 'override' in data:
        override = data["override"]
    logger.info(f'Schema reset type is {override}')

    create_db = False
    if not os.path.exists(database_file):
        create_db = True
    elif override:
        create_db = True
        os.remove(database_file)

    if not override and not create_db:
        logger.info(f"Database already preset at {database_file}")
        return json.dumps({'Database Error': f"Database already preset at {database_file}"}), 500

    logger.info(f"API will create the schema")

    conn = sqlite3.connect(database_file)
    query = (
        f"CREATE TABLE EMPLOYEE"
        f" (ID INT PRIMARY KEY NOT NULL,"
        f" NAME TEXT NOT NULL,"
        f" JOB_NAME INT NOT NULL,"
        f" DEPT_ID INT NOT NULL,"
        f" PACKAGE INT NOT NULL);"
    )
    conn.execute(query)

    query = (
        f"CREATE TABLE DEPARTMENT"
        f" (ID INT PRIMARY KEY NOT NULL,"
        f" NAME TEXT NOT NULL);"
    )
    conn.execute(query)
    conn.close()
    logger.info(f"Schema created at path {database_file}")
    return json.dumps({'Database success': f"Schema created at path {database_file}"}), 200


def execute_query():
    data = request.get_json()

    if not data or 'query' not in data:
        msg = "Failed to get query in API call"
        logger.error(msg)
        return json.dumps(msg), 500

    query = data["query"]
    if not query:
        msg = "Failed to get query in API call"
        logger.error(msg)
        return json.dumps(msg), 500

    conn = sqlite3.connect(database_file)
    cursor = conn.execute(query)
    conn.commit()

    columns = cursor.description
    results = [{columns[index][0]:column for index,
                column in enumerate(value)} for value in cursor.fetchall()]

    # results = cursor.fetchall()

    if cursor:
        cursor.close()
    if conn:
        conn.close()

    return json.dumps({'results': results}), 200


def register(app, context_name):
    logger.info(f'Registering routes for {context_name}')
    app.add_url_rule(rule=f'/{context_name}/create_schema',
                     endpoint='create_schema',
                     methods=['POST'],
                     view_func=create_employee_schema)
    app.add_url_rule(rule=f'/{context_name}/execute/query',
                     endpoint='query',
                     methods=['POST'],
                     view_func=execute_query)
