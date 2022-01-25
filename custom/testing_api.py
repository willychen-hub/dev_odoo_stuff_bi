import json
import logging

import pandas as pd
from flask import Flask, jsonify, request
from library_ver3.exception_handler import format_error_traceback
from library_ver3.pg_sql import PGSqlTool

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/get_receiver_info", methods=["GET"])
def get_receiver_info():
    test_cur = PGSqlTool("prod", "db_dw_reader")
    raw_sql = """
              select oid, name from _ods_test.export_email_main
              """
    a = test_cur.query(raw_sql)
    test_cur.close()
    return json.dumps(a)


@app.route("/update_record", methods=["POST"])
def update_record():
    try:
        # Getting data from requests
        records_data = json.loads(request.get_data())

        # Connect to DB
        test_cur = PGSqlTool("prod", "db_dw_writer")

        update_raw_sql = """
                          update _ods_test.export_email_main
                          set name = %s,
                             modify_user = %s,
                             modify_date = %s
                          where oid = %s
                          """

        update_data = (
            records_data["name"],
            records_data["login_user_email"],
            records_data["update_time"],
            records_data["dw_oid"],
        )
        test_cur.non_query(update_raw_sql, "update", update_data)

        search_raw_sql = f"""
                            select name from _ods_test.export_email_main
                            where oid = {records_data['dw_oid']}
                          """

        query_result_data = test_cur.query(search_raw_sql)
        test_cur.close()

        return json.dumps(query_result_data)
    except Exception as e:
        logging.error(e)
        print(format_error_traceback(e))


@app.route("/create_records", methods=["POST"])
def create_records():
    try:
        # Getting data from requests
        records_data = json.loads(request.get_data())

        # Insert new data to table
        test_cur = PGSqlTool("prod", "db_dw_writer")
        insert_raw_sql = """
                  insert into _ods_test.export_email_main
                  (name, create_date, create_user, modify_date, modify_user, service_project, export_status, last_export_date)
                  values %s
                  """
        insert_value = [
            (
                records_data["name"],
                records_data["insert_time"],
                records_data["login_user_email"],
                records_data["insert_time"],
                records_data["login_user_email"],
                "TESTING",
                "SEND",
                records_data["insert_time"],
            )
        ]
        test_cur.non_query(insert_raw_sql, "insert", insert_value)
        search_raw_sql = f"""
              select oid, name from _ods_test.export_email_main
              where name = '{records_data["name"]}'
              and create_user = '{records_data["login_user_email"]}'
              and modify_user = '{records_data["login_user_email"]}'
              """
        query_result_data = test_cur.query(search_raw_sql)

        test_cur.close()
        return json.dumps(query_result_data)
    except Exception as e:
        logging.error(e)
        print(format_error_traceback(e))
        return {}


app.run()
