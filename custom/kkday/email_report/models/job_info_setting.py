# -*- coding: utf-8 -*-
import json
import logging

import pandas as pd
import requests
from odoo import api, fields, models


# This is to create a the column for later usage.
class JobInfoSetting(models.Model):
    _name = "bi.email.report.job.info.setting"
    _description = "The list page of user setting"

    # Show in tree view
    reciever_name = fields.Char("reciever_name", required=True)
    reciever_email = fields.Char("reciever_email", required=True)
    email_subject = fields.Char("email_subject", required=True)
    service_project = fields.Char("service_project")
    sending_frequency = fields.Char("sending_frequency")
    sending_time = fields.Char("sending_time")
    freq_json = fields.Char("freq_json")
    start_date = fields.Char("start_date")
    end_date = fields.Char("end_date")
    export_flag = fields.Boolean("export_flag", store=True)

    # Not show in tree view
    dw_job_oid = fields.Char("dw_job_oid")
    dw_receiver_oid = fields.Char("dw_receiver_oid")
    email_content = fields.Char("email_content", required=True)
    attachment_location = fields.Char("attachment_location")
    attachment_setting = fields.Char("attachment_setting")
    creator_email = fields.Char("creator_email")
    modifier_email = fields.Char("modifier_email")

    # @api.model
    # def create(self, vals_lst):
    #     logging.info(vals_lst)
    #     headers = {
    #         "Content-Type": "application/json",
    #     }

    #     data = json.dumps(vals_lst)

    #     response = requests.post(
    #         "http://127.0.0.1:5000/create_records", headers=headers, data=data
    #     )
    #     logging.info("hihihi")

    #     # response = requests.get("http://127.0.1.:5000/search_data")

    #     res = super(UserInfoSetting, self).create(vals_lst)
    #     return res

    # def write(self, vals_dict):
    #     res = super(UserInfoSetting, self).write(vals_dict)
    #     return res

    # def unlink(self):
    #     logging.info(self)
    #     for i in self:
    #         logging.info(i)
    #         logging.info(type(i))
    #         logging.info(i.name)
    #     return super(UserInfoSetting, self).unlink()

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        if view_type == "form":
            # Getting data from DW table
            query_result = json.loads(
                requests.get("http://127.0.0.1:5000/get_job_info").text
            )

            # Change result to dataframe
            query_df = pd.DataFrame(
                query_result["results"], columns=query_result["columns"]
            )

            # Truncate table
            self.env.cr.execute(
                "Truncate table bi_email_report_job_info_setting RESTART IDENTITY"
            )

            logging.info(query_df)
            logging.info(query_df.columns)
            logging.info("")
            insert_data_lst = query_df.to_dict("records")
            logging.info(insert_data_lst)

            # Create data to Odoo table
            self.env["bi.email.report.job.info.setting"].create(
                insert_data_lst
            )

        res = super(JobInfoSetting, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        return res
