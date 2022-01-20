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
    default_email = fields.Text(size=150)

    # Checkbox
    services_name_str = fields.Many2many("service", string="Services List")

    @api.model
    def create(self, vals_lst):
        logging.info(vals_lst)
        res = super(UserInfoSetting, self).create(vals_lst)
        headers = {
            "Content-Type": "application/json",
        }

        service_id_lst = vals_lst["services_name_str"][0][2]
        service_dict_lst = self.env["service"].search_read(
            [("id", "in", service_id_lst)]
        )

        service_name_lst = [
            service_dict["services_name_str"]
            for service_dict in service_dict_lst
        ]

        vals_lst["services_name_str"] = service_name_lst
        data = json.dumps(vals_lst)

        response = requests.post(
            "http://127.0.0.1:5000/foo", headers=headers, data=data
        )
        return res

    def write(self, vals_dict):
        if "services_name_str" in vals_dict:
            services_id_lst = vals_dict["services_name_str"][0][2]
            services_dict = self._mapping_service_info("id", services_id_lst)
            pass
        else:
            pass
        logging.info("After")
        logging.info(self.name)

        logging.info(f"name: {self.name}")
        logging.info(f"dw_oid: {self.dw_oid}")
        logging.info(f"default_email: {self.default_email}")
        logging.info(f"services_name_str: {self.services_name_str}")
        res = super(UserInfoSetting, self).write(vals_dict)
        return res
        # logging.info("Vals_lst")
        # logging.info(vals_lst)
        # if "services_name_str" in vals_l
        # data = vals_lst



        # for a in self.services_name_str:
        #     logging.info(a)
        #     logging.info(type(a))
        #     logging.info(a.services_name_str)

    def unlink(self):
        logging.info(self)
        for i in self:
            logging.info(i)
            logging.info(type(i))
            logging.info(i.name)
        return super(UserInfoSetting, self).unlink()

    def _mapping_service_info(self, search_type, search_value):
        service_info_dict = self.env["service"].search_read(
            [
                (
                    search_type,
                    "in",
                    search_value,
                )
            ]
        )
        service_info_df = pd.DataFrame(service_info_dict)
        if search_type == "services_name_str":
            service_dict = dict(
                zip(
                    service_info_df.services_name_str,
                    service_info_df.id,
                )
            )
        elif search_type == "id":
            service_dict = dict(
                zip(
                    service_info_df.id,
                    service_info_df.services_name_str,
                )
            )
        return service_dict

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
            # Change the string to Capital
            query_df["service_project"] = query_df["service_project"].apply(
                lambda x: x.capitalize()
            )
            # Rename columns
            query_df.rename(
                columns={
                    "create_user": "default_email",
                    "service_project": "services_name_str",
                    "oid": "dw_oid",
                },
                inplace=True,
            )
            # Truncate table
            self.env.cr.execute(
                "Truncate table bi_email_report_user_info_setting_service_rel, bi_email_report_user_info_setting"
            )
            # Search for service id
            service_dict = self._mapping_service_info(
                "services_name_str",
                query_df["services_name_str"].values.tolist(),
            )
            # Combine data together
            query_df = (
                query_df.groupby(["name", "default_email"])
                .agg(tuple)
                .applymap(list)
                .reset_index()
            )
            # Convert data to fit Odoo table
            query_df["services_name_str"] = query_df["services_name_str"].apply(
                lambda x: [service_dict[y] for y in x]
            )
            query_df["services_name_str"] = query_df["services_name_str"].apply(
                lambda x: [[6, False, x]]
            )
            query_df["dw_oid"] = query_df["dw_oid"].apply(
                lambda x: str(x)[1:-1].replace(" ", "")
            )

            logging.info(query_df)
            logging.info("")
            logging.info("")
            insert_data_lst = query_df.to_dict("records")
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


class Services(models.Model):
    _name = "service"
    _description = "The list of services get from requests"
    # To prevent show model,id instead value on view.
    _rec_name = "services_name_str"

    logging.info("Inside of services")
    services_name_str = fields.Char("Services")

    def init(self):
        logging.info("Inside of Services's init")
        logging.info("Start Services API")
        query_result = requests.get("http://127.0.0.1:5000/").text
        query_dict = json.loads(query_result)
        logging.info("End Services API")

        logging.info("Change to dataframe")
        records_df = pd.DataFrame(query_dict)

        logging.info("Query from table")
        existing_data_filter = self.sudo().search_read(
            [
                (
                    "services_name_str",
                    "in",
                    records_df["services_name_str"].values.tolist(),
                )
            ]
        )
        existing_df = pd.DataFrame(existing_data_filter)
        if existing_df.empty:
            logging.info("Empty results")
            existing_df = pd.DataFrame(columns=["services_name_str"])

        df = pd.merge(
            records_df,
            existing_df,
            on=["services_name_str"],
            how="left",
            indicator=True,
        )
        df = (
            df.query("_merge != 'both'")
            .drop("_merge", axis=1)
            .reset_index(drop=True)
        )
        logging.info(df.to_dict("records"))
        logging.info("Inserting data to table")
        insert_dict = [
            {"services_name_str": record["services_name_str"]}
            for record in df.to_dict("records")
        ]
        self.env["service"].create(insert_dict)
