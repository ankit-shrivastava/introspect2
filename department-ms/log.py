#!/usr/bin/env python

"""
File to handle the logging mehcanism to file as per handlers.
"""

import os
import json
from logging.config import dictConfig

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_ROOT = ROOT

dept_home = os.environ.get('DEPT_HOME') if 'DEPT_HOME' in os.environ else None
if dept_home:
    LOG_ROOT = dept_home


def get_json_data(file_name):
    data = None

    if (os.path.exists(file_name)):
        print(f'Reading JSON file : {file_name}')
        with open(file_name, 'r') as f:
            data = f.read()
        return json.loads(data)
    else:
        print(f'JSON file does not exists : {file_name}')
        return None


def initialize_logging():
    """
    A function to initialize the Python Logger.
    """
    config_file = os.path.join(ROOT, "logging.conf.json")
    log_root = os.path.join(LOG_ROOT, "logs")

    log_info_file = os.path.join(log_root, f"dept.info.log")
    log_error_file = os.path.join(log_root, f"dept.error.log")
    os.makedirs(log_root, exist_ok=True)

    log_configs = get_json_data(file_name=config_file)
    log_configs = str(log_configs).replace("{{LOG_INFO}}", log_info_file)
    log_configs = log_configs.replace("{{LOG_ERROR}}", log_error_file)

    dictConfig(eval(log_configs))
