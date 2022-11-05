#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
from os.path import join, dirname
import sql
import MySQLdb
import datetime

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ACCESS_LOG_TABLE = os.environ['ACCESS_LOG_TABLE']

def record_access(request, id_str):
    dt_now = datetime.datetime.now()
    query = f'insert into {ACCESS_LOG_TABLE} values(\"{request.remote_addr}\",\"' + dt_now.strftime('%Y-%m-%d %H:%M:%S') + '\",\"' + id_str + '\")'
    sql.exec_query(query)