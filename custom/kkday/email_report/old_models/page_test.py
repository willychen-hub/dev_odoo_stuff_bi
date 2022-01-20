# -*- coding: utf-8 -*-
import logging
import json 
import pandas as pd


import requests
from odoo import api, fields, models, tools


# This is to create a the column for later usage.
class PageTest(models.Model):
    _name = "er.test.abstract.model.with.api"
    _description = "This is to check if getting API data "
    _auto = False

    var_1 = fields.Char("Var 1")

    def init(self):
        logging.info('inside of init.')
        tools.drop_view_if_exists(
            self.env.cr, "er_test_abstract_model_with_api"
        )
        a = requests.get("http://127.0.0.1:5000/").text
        logging.info(a)
        df = pd.DataFrame(a)
        logging.info("show string")
        columns_lst = (df.columns)
        logging.info(columns_lst)
        raw_sql = """
                  CREATE OR REPLACE VIEW er_test_abstract_model_with_api AS (
                  """

        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW er_test_abstract_model_with_api AS (
                SELECT  *
                FROM    (
                        VALUES
                        (1, '2'),
                        (2, '4')
                        ) AS q (id, var_1))
            """
            # """
            # CREATE OR REPLACE VIEW er_test_abstract_model_with_api AS (
            # SELECT
            #     1 AS id,
            #     'k1' AS var_1)
            # """
        )
        logging.info("this is inside of init.")
