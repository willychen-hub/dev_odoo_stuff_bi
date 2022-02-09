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
    query_result = test_cur.query(raw_sql)
    test_cur.close()
    return json.dumps(query_result)


@app.route("/update_receiver_record", methods=["POST"])
def update_receiver_record():
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


@app.route("/create_receiver_records", methods=["POST"])
def create_receiver_records():
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
        a = test_cur.non_query(insert_raw_sql, "insert", insert_value)

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


@app.route("/get_job_info", methods=["GET"])
def get_job_info():
    test_cur = PGSqlTool("prod", "db_dw_reader")
    raw_sql = """
              select
                a.oid as dw_job_oid,
                main_oid as dw_receiver_oid,
                b.name as reciever_name,
                email as reciever_email,
                email_subject,
                email_content,
                attachment_source as service_project,
                attachment_location,
                attachment_setting->>'workbook_link' as workbook_link,
                attachment_setting->>'type' as file_type,
                attachment_setting->>'filename' as file_name,
                attachment_setting->>'pagesize' as page_size,
                attachment_setting->>'pagelayout' as page_layout,
                attachment_setting->>'supplier_oid' as supplier_oid,
                attachment_setting->>'workbook_link' as workbook_link,
                attachment_setting->>'width' as width,
                attachment_setting->>'height' as height,
                attachment_setting->>'file_s3_location' as file_s3_location,
                sending_time,
                freq_type as frequency_type,
                freq_json->>'freq' as sending_frequency,
                to_char(start_send_dt_tw, 'YYYY-MM-DD') as start_date,
                to_char(end_send_dt_tw, 'YYYY-MM-DD') as end_date,
                export_flag,
                a.create_user as creator_email,
                a.modify_user as modifier_email
              from _ods_test.export_email_setting a
              join _ods_test.export_email_main b on a.main_oid = b.oid
              """

    query_result = test_cur.query(raw_sql)
    test_cur.close()
    return json.dumps(query_result)


@app.route("/create_job_records", methods=["POST"])
def create_job_records():
    try:
        # Getting data from requests
        records_data = json.loads(request.get_data())
        print(records_data)
        test_cur = PGSqlTool("prod", "db_dw_writer")
        insert_raw_sql = """
                  insert into _ods_test.export_email_setting
                  (main_oid, email, email_subject, email_content, attachment_source,
                  attachment_location, sending_time, freq_type, freq_json,
                  start_send_dt_tw, end_send_dt_tw, export_flag, create_date,
                  create_user, modify_date, modify_user, attachment_setting)
                  values %s
                  """
        insert_value = [
            records_data["dw_receiver_oid"],
            records_data["reciever_email"],
            records_data["email_subject"],
            records_data["email_content"],
            records_data["service_project"],
            "send_prj_files",
            records_data["sending_time"],
            records_data["frequency_type"],
            json.dumps({"freq_json": records_data["sending_frequency"]}),
            records_data["start_date"],
            records_data["end_date"],
            records_data["export_flag"],
            records_data["insert_time"],
            records_data["login_user_email"],
            records_data["insert_time"],
            records_data["login_user_email"],
        ]
        if "tableau" == records_data["service_project"]:
            attachment_setting = {
                "type": records_data["file_type"],
                "supplier_oid": records_data["dw_receiver_oid"],
                "filename": records_data["file_name"],
                "pagesize": records_data["page_size"],
                "pagelayout": records_data["page_layout"],
                "width": records_data["width"],
                "height": records_data["height"],
                "workbook_link": records_data["workbook_link"],
            }
        elif "s3" == records_data["service_project"]:
            attachment_setting = {
                "filename": records_data["file_name"],
                "supplier_oid": records_data["dw_receiver_oid"],
                "file_s3_location": records_data["file_s3_location"],
            }
        insert_value.append(json.dumps(attachment_setting))
        a = test_cur.non_query(insert_raw_sql, "insert", [tuple(insert_value)])

        search_raw_sql = f"""
              select
                a.oid as dw_job_oid,
                main_oid as dw_receiver_oid,
                b.name as reciever_name,
                email as reciever_email,
                email_subject,
                email_content,
                attachment_source as service_project,
                attachment_location,
                attachment_setting->>'workbook_link' as workbook_link,
                attachment_setting->>'type' as file_type,
                attachment_setting->>'filename' as file_name,
                attachment_setting->>'pagesize' as page_size,
                attachment_setting->>'pagelayout' as page_layout,
                attachment_setting->>'supplier_oid' as supplier_oid,
                attachment_setting->>'workbook_link' as workbook_link,
                attachment_setting->>'width' as width,
                attachment_setting->>'height' as height,
                attachment_setting->>'file_s3_location' as file_s3_location,
                sending_time,
                freq_type as frequency_type,
                freq_json->>'freq_json' as sending_frequency,
                to_char(start_send_dt_tw, 'YYYY-MM-DD') as start_date,
                to_char(end_send_dt_tw, 'YYYY-MM-DD') as end_date,
                export_flag,
                a.create_user as creator_email,
                a.modify_user as modifier_email
              from _ods_test.export_email_setting a
              join _ods_test.export_email_main b on a.main_oid = b.oid
              where main_oid = {records_data["dw_receiver_oid"]}
              and email = '{records_data["reciever_email"]}'
              and email_subject = '{records_data["email_subject"]}'
              """
        query_result_data = test_cur.query(search_raw_sql)
        print(query_result_data)

        test_cur.close()
        return json.dumps(query_result_data)

    except Exception as e:
        logging.error(e)
        print(format_error_traceback(e))


@app.route("/update_job_records", methods=["POST"])
def update_job_records():
    try:
        # Getting data from requests
        records_data = json.loads(request.get_data())

        # Connect to DB
        test_cur = PGSqlTool("prod", "db_dw_writer")

        update_raw_sql = """
                          update _ods_test.export_email_setting set
                          """

        # Adding condition
        update_data = []
        attachment_setting = {}
        for r_key, r_value in records_data.items():
            if r_key == "dw_job_oid":
                pass
            elif r_key == "reciever_email" and r_value:
                update_raw_sql += "email = %s,"
                update_data.append(r_value)
            elif (
                r_key
                in (
                    "email_subject",
                    "email_content",
                    "sending_time",
                    "export_flag",
                )
                and r_value
            ):
                update_raw_sql += f"{r_key} = %s,"
                update_data.append(r_value)
            elif r_key == "service_project" and r_value:
                update_raw_sql += f"attachment_source = %s,"
                update_data.append(r_value)
            elif r_key == "frequency_type" and r_value:
                update_raw_sql += f"freq_type = %s,"
                update_data.append(r_value)
            elif r_key == "sending_frequency" and r_value:
                update_raw_sql += (
                    "freq_json = jsonb_set(freq_json, '{freq}', %s, false),"
                )
                update_data.append(r_value)
            elif r_key == "start_date" and r_value:
                update_raw_sql += f"start_send_dt_tw = %s,"
                update_data.append(r_value)
            elif r_key == "end_date" and r_value:
                update_raw_sql += f"end_send_dt_tw = %s,"
                update_data.append(r_value)
            elif r_key == "login_user_email" and r_value:
                update_raw_sql += f"modify_user = %s,"
                update_data.append(r_value)
            elif r_key == "update_time" and r_value:
                update_raw_sql += f"modify_date = %s,"
                update_data.append(r_value)
            elif r_key == "file_s3_location" and r_value:
                attachment_setting["file_s3_location"] = r_value
            elif r_key == "workbook_link" and r_value:
                attachment_setting["workbook_link"] = r_value
            elif r_key == "file_type" and r_value:
                attachment_setting["type"] = r_value
            elif r_key == "file_name" and r_value:
                attachment_setting["filename"] = r_value
            elif r_key == "page_size" and r_value:
                attachment_setting["pagesize"] = r_value
            elif r_key == "page_layout" and r_value:
                attachment_setting["pagelayout"] = r_value
            elif r_key == "width" and r_value:
                attachment_setting["width"] = r_value
            elif r_key == "height" and r_value:
                attachment_setting["height"] = r_value

        if len(attachment_setting) > 0:
            update_raw_sql += f"attachment_setting = attachment_setting || '{json.dumps(attachment_setting)}'"
        else:
            update_raw_sql = update_raw_sql[:-1]

        update_raw_sql += f" where oid = {records_data['dw_job_oid']}"

        test_cur.non_query(update_raw_sql, "update", update_data)

        search_raw_sql = f"""
                            select
                                a.oid as dw_job_oid,
                                main_oid as dw_receiver_oid,
                                b.name as reciever_name,
                                email as reciever_email,
                                email_subject,
                                email_content,
                                attachment_source as service_project,
                                attachment_location,
                                attachment_setting->>'workbook_link' as workbook_link,
                                attachment_setting->>'type' as file_type,
                                attachment_setting->>'filename' as file_name,
                                attachment_setting->>'pagesize' as page_size,
                                attachment_setting->>'pagelayout' as page_layout,
                                attachment_setting->>'supplier_oid' as supplier_oid,
                                attachment_setting->>'workbook_link' as workbook_link,
                                attachment_setting->>'width' as width,
                                attachment_setting->>'height' as height,
                                attachment_setting->>'file_s3_location' as file_s3_location,
                                sending_time,
                                freq_type as frequency_type,
                                freq_json->>'freq' as sending_frequency,
                                to_char(start_send_dt_tw, 'YYYY-MM-DD') as start_date,
                                to_char(end_send_dt_tw, 'YYYY-MM-DD') as end_date,
                                export_flag,
                                a.create_user as creator_email,
                                a.modify_user as modifier_email
                            from _ods_test.export_email_setting a
                            join _ods_test.export_email_main b on a.main_oid = b.oid
                            where a.oid = {records_data['dw_job_oid']}
                          """
        query_result_data = test_cur.query(search_raw_sql)
        test_cur.close()

        return json.dumps(query_result_data)
    except Exception as e:
        logging.error(e)
        print(format_error_traceback(e))


app.run()
