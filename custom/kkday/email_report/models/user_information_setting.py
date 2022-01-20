# -*- coding: utf-8 -*-
import json
import logging

import pandas as pd
import requests
from odoo import api, fields, models


# This is to create a the column for later usage.
class UserInfoSetting(models.Model):
    _name = "bi.email.report.user.info.setting"
    _description = "The list page of user setting"

    dw_oid = fields.Char("ID for DW")
    name = fields.Char("Reciever Name", required=True)

    @api.model
    def create(self, vals_lst):
        logging.info(vals_lst)
        headers = {
            "Content-Type": "application/json",
        }

        data = json.dumps(vals_lst)

        response = requests.post(
            "http://127.0.0.1:5000/create_records", headers=headers, data=data
        )
        logging.info("hihihi")

        # response = requests.get("http://127.0.1.:5000/search_data")

        res = super(UserInfoSetting, self).create(vals_lst)
        return res

    def write(self, vals_dict):
        res = super(UserInfoSetting, self).write(vals_dict)
        return res

    def unlink(self):
        logging.info(self)
        for i in self:
            logging.info(i)
            logging.info(type(i))
            logging.info(i.name)
        return super(UserInfoSetting, self).unlink()

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        if view_type == "form":
            # Getting data from DW table
            query_result = json.loads(
                requests.get("http://127.0.0.1:5000/get_receiver_info").text
            )

            # Change result to dataframe
            query_df = pd.DataFrame(
                query_result["results"], columns=query_result["columns"]
            )

            # Rename columns
            query_df.rename(columns={"oid": "dw_oid"}, inplace=True)

            # Truncate table
            self.env.cr.execute(
                # "Truncate table bi_email_report_user_info_setting_service_rel, bi_email_report_user_info_setting RESTART IDENTITY"
                "Truncate table bi_email_report_user_info_setting RESTART IDENTITY"
            )

            logging.info(query_df)
            logging.info("")
            logging.info("")
            insert_data_lst = query_df.to_dict("records")
            logging.info(insert_data_lst)

            # Create data to Odoo table
            self.env["bi.email.report.user.info.setting"].create(
                insert_data_lst
            )

        res = super(UserInfoSetting, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        return res
