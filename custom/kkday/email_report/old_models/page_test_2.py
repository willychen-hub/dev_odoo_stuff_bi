# -*- coding: utf-8 -*-
import json
import logging

import pandas as pd
import requests
from odoo import api, fields, models, tools


# This is to check if the insert data works
class PageTestTwo(models.Model):
    _name = "er.test.model.with.table.insert.api.data"
    _description = (
        "This is to check if we can insert data to table when init happens"
    )

    var_1 = fields.Char("Var 1")

    def init(self):
        logging.info(
            "=========================================================="
        )
        logging.info("Inside of Init")

        # a = requests.get("http://127.0.0.1:5000/").text
        # Why do we need to drop data form DB?
        records_lst = [
            {"id": 1, "var_1": "dict1"},
            {"id": 2, "var_1": "dict2"},
            {"id": 9, "var_1": "dict99"},
            {"id": 9, "var_1": "dict88"},
        ]
        records_df = pd.DataFrame(records_lst)
        logging.info(records_df["var_1"])
        existing_data_filter = self.sudo().search_read(
            [("var_1", "in", records_df["var_1"].values.tolist())]
        )
        existing_df = pd.DataFrame(existing_data_filter)
        df = pd.merge(
            records_df,
            existing_df,
            on=["var_1"],
            how="left",
            indicator=True,
        )

        logging.info("Df after merges")
        df = (
            df.query("_merge != 'both'")
            .drop("_merge", axis=1)
            .reset_index(drop=True)
        )
        logging.info(df)
        logging.info("DF to dictionary")
        logging.info(df[["id_x", "var_1"]].to_dict("records"))
        a = df[["var_1"]].to_dict("records")
        logging.info("")
        logging.info("")
        logging.info("")

        # Remove data from dataframe
        # for record in records_lst:
        #     a = record["var_1"]
        #     existing_flag = self.sudo().search_read([("var_1", "==", a)])
        #     logging.info(existing_flag)
        #     logging.info(record["var_1"])
        # logging.info(f"{record} : {existing_product}")
        self.env["er.test.model.with.table.insert.api.data"].create(
            a
        )
        logging.info(
            "=========================================================="
        )
        # record = super(PageTestTwo, self).create(
        #     [{"id": 1, "var_1": "dict1"}, {"id": 2, "var_1": "dict2"}]
        # )
        self.env.cr.commit()
