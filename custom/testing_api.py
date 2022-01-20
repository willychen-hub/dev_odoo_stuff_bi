import json
import logging

import pandas as pd
from flask import Flask, jsonify, request
from library_ver3.pg_sql import PGSqlTool

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/get_receiver_info", methods=["GET"])
def get_receiver_info():
    test_cur = PGSqlTool("prod", "db_dw_writer")
    raw_sql = """
              select oid, name from export_email_main
              where oid in (1,3)
              """
    a = test_cur.query(raw_sql)
    return json.dumps(a)


@app.route("/", methods=["GET"])
def home():
    studentData = {"services_name_str": ["S3", "Tableau", "Big Query"]}
    return json.dumps(studentData)


@app.route("/create_records", methods=["POST"])
def create_records():
    try:
        records_data = json.loads(request.get_data())
        print(records_data)
        return jsonify(records_data)
    except Exception as e:
        print(e)
        return {}


app.run()
