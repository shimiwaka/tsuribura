#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
from os.path import join, dirname
import MySQLdb
import datetime

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ACCESS_LOG_TABLE = os.environ['ACCESS_LOG_TABLE']
DB_NAME = os.environ['DB_NAME']
DB_HOST = os.environ['DB_HOST']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

def exec_query(query):
    try:
        conn = MySQLdb.connect(
            user=DB_USER,
            passwd=DB_PASSWORD,
            host=DB_HOST,
            db=DB_NAME,
            charset="utf8mb4")
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        conn.close()
    except Exception as e:
        return False
    return True

def exec_query_with_reply(query):
    ret_array = []
    try:
        conn = MySQLdb.connect(
            user=DB_USER,
            passwd=DB_PASSWORD,
            host=DB_HOST,
            db=DB_NAME,
            charset="utf8mb4")
        c = conn.cursor()
        c.execute(query)
        for row in c.fetchall():
            ret_array.append(row)
        conn.close()
    except Exception as e:
        return ret_array
    return ret_array