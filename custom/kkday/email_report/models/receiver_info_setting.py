# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

import pandas as pd
import requests
from odoo import api, fields, models


# This is to create a the column for later usage.
class ReceiverInfoSetting(models.Model):
    _name = "bi.email.report.receiver.info.setting"
    _description = "The list page of Receiver setting"

    dw_oid = fields.Char("ID for DW")
    name = fields.Char("Reciever Name", required=True)

    @api.model
    def create(self, vals_dict: dict):
        """
        Insert the data to DW table and query from DW table then insert into Odoo table.

        Args:
            vals_dict (Dictionary): The data need to insert to Odoo and DW table.

        """
        headers = {
            "Content-Type": "application/json",
        }

        logging.info(vals_dict)

        # Check if the data already inside of DW table.
        if "dw_oid" not in vals_dict.keys():
            vals_dict["login_user_email"] = self.env.user.email
            vals_dict["insert_time"] = str(datetime.now())
            data_dict = json.dumps(vals_dict)
            response = requests.post(
                "http://127.0.0.1:5000/create_records",
                headers=headers,
                data=data_dict,
            )
            data_info = json.loads(response.text)
            query_df = pd.DataFrame(
                data_info["results"], columns=data_info["columns"]
            )
            query_df.rename(columns={"oid": "dw_oid"}, inplace=True)
            data_dict = query_df.to_dict("records")
        else:
            data_dict = vals_dict

        res = super(ReceiverInfoSetting, self).create(data_dict)
        return res

    def write(self, vals_dict):
        headers = {
            "Content-Type": "application/json",
        }
        logging.info(self.dw_oid)
        vals_dict["dw_oid"] = self.dw_oid
        vals_dict["update_time"] = str(datetime.now())
        vals_dict["login_user_email"] = self.env.user.email
        data_dict = json.dumps(vals_dict)
        logging.info(vals_dict)
        response = requests.post(
            "http://127.0.0.1:5000/update_record",
            headers=headers,
            data=data_dict,
        )
        data_info = json.loads(response.text)
        logging.info(data_info)
        query_df = pd.DataFrame(
            data_info["results"], columns=data_info["columns"]
        )
        update_dict = query_df.to_dict("records")[0]
        logging.info(update_dict)

        res = super(ReceiverInfoSetting, self).write(update_dict)
        return res

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
                "Truncate table bi_email_report_receiver_info_setting RESTART IDENTITY"
            )

            insert_data_lst = query_df.to_dict("records")

            # Create data to Odoo table
            self.env["bi.email.report.receiver.info.setting"].create(
                insert_data_lst
            )

        res = super(ReceiverInfoSetting, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        return res
