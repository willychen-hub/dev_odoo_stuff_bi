# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

import pandas as pd
import re
import requests
from odoo import api, fields, models
from odoo.exceptions import ValidationError


# This is to create a the column for later usage.
class JobInfoSetting(models.Model):
    _name = "bi.email.report.job.info.setting"
    _description = "The list page of user setting"

    # Column Define
    # Show in tree view
    reciever_name = fields.Selection(
        selection=lambda self: self._all_receiver_name(),
        string="reciever_name",
        default="0",
        required=True,
        help="Choose the receiver'name.",
    )
    reciever_email = fields.Char(
        "reciever_email",
        required=True,
        help="The emails of the receiver. Multiple email can be seperated by comma.",
    )
    email_subject = fields.Char(
        "email_subject", required=True, help="The topic of the email."
    )
    sending_frequency = fields.Char(
        "sending_frequency", help="When to send the email."
    )
    sending_time = fields.Selection(
        selection=lambda self: self._all_sending_time(),
        string="sending time",
        default="0",
        help="What time to send out the email.",
    )
    frequency_type = fields.Selection(
        selection=lambda self: self._default_freq_type(),
        string="frequency_type",
        default="0",
        help="How often to send the email.",
    )
    service_project = fields.Selection(
        selection=lambda self: self._default_service_type(),
        string="service_project",
        default="0",
        help="The service of the data need to send.",
    )
    start_date = fields.Date("start_date", help="When to start sending email.")
    end_date = fields.Date("end_date", help="When to stop sending email.")
    export_flag = fields.Boolean("export_flag", default=True, help="If need to start sending email.")

    # Not show in tree view
    dw_job_oid = fields.Char("dw_job_oid")
    dw_receiver_oid = fields.Char("dw_receiver_oid")
    email_content = fields.Text("email_content", required=True)
    attachment_location = fields.Char("attachment_location")
    workbook_link = fields.Char("workbook_link")

    file_type = fields.Selection(
        selection=lambda self: self._default_file_type(),
        string="file_type",
        default="0",
    )

    file_name = fields.Char("file_name")
    page_size = fields.Selection(
        selection=lambda self: self._default_page_size_type(),
        string="page_size",
        default="0",
    )

    page_layout = fields.Selection(
        selection=lambda self: self._default_page_layout_type(),
        string="page_layout",
        default="0",
    )
    supplier_oid = fields.Char("supplier_oid")
    width = fields.Integer("width")
    height = fields.Integer("height")
    file_s3_location = fields.Char("file_s3_location")
    creator_email = fields.Char("creator_email")
    modifier_email = fields.Char("modifier_email")

    # CRUD
    @api.model
    def create(self, vals_dict):
        headers = {
            "Content-Type": "application/json",
        }

        # Check if the data already inside of DW table
        if "dw_job_oid" not in vals_dict.keys():
            vals_dict["login_user_email"] = self.env.user.email
            vals_dict["insert_time"] = str(datetime.now())
            vals_dict["dw_receiver_oid"] = self.env[
                "bi.email.report.receiver.info.setting"
            ].search_read([("name", "=", vals_dict["reciever_name"])])[0][
                "dw_oid"
            ]
            vals_dict["start_date"] = str(vals_dict["start_date"])
            vals_dict["end_date"] = str(vals_dict["end_date"])
            if vals_dict["frequency_type"] == "daily":
                vals_dict["sending_frequency"] = 1

            data = json.dumps(vals_dict)

            response = requests.post(
                "http://127.0.0.1:5000/create_job_records",
                headers=headers,
                data=data,
            )
            data_info = json.loads(response.text)
            query_df = pd.DataFrame(
                data_info["results"], columns=data_info["columns"]
            )
            query_df.rename(columns={"oid": "dw_oid"}, inplace=True)
            insert_dict = query_df.to_dict("records")
        else:
            insert_dict = vals_dict

        res = super(JobInfoSetting, self).create(insert_dict)
        return res

    def write(self, vals_dict):
        headers = {
            "Content-Type": "application/json",
        }
        vals_dict["update_time"] = str(datetime.now())
        vals_dict["login_user_email"] = self.env.user.email
        vals_dict["dw_job_oid"] = self.dw_job_oid
        data_dict = json.dumps(vals_dict)
        response = requests.post(
            "http://127.0.0.1:5000/update_job_records",
            headers=headers,
            data=data_dict,
        )
        data_info = json.loads(response.text)
        query_df = pd.DataFrame(
            data_info["results"], columns=data_info["columns"]
        )
        update_dict = query_df.to_dict("records")[0]

        res = super(JobInfoSetting, self).write(update_dict)
        return res

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
                "Truncate bi_email_report_job_info_setting RESTART IDENTITY"
            )

            insert_data_lst = query_df.to_dict("records")

            # Create data to Odoo table
            self.env["bi.email.report.job.info.setting"].create(insert_data_lst)

        res = super(JobInfoSetting, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        return res

    # Other function
    def _default_freq_type(self):
        freq_type_lst = [
            ("0", "選擇發送頻率"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
        ]
        return freq_type_lst

    def _default_service_type(self):
        service_type_lst = [
            ("0", "選擇服務"),
            ("s3", "S3"),
            ("tableau", "Tableau"),
        ]
        return service_type_lst

    def _default_file_type(self):
        file_type_lst = [
            ("0", "選擇檔案格式"),
            ("img", "Img"),
            ("pdf", "PDF"),
            ("fullpdf", "Full PDF"),
        ]
        return file_type_lst

    def _default_page_size_type(self):
        page_size_lst = [
            ("0", "選擇Page Size"),
            ("a3", "A3"),
            ("a4", "A4"),
            ("a5", "A5"),
            ("b5", "B5"),
            ("executive", "Executive"),
            ("folio", "Folio"),
            ("ledger", "Ledger"),
            ("letter", "Letter"),
            ("note", "Note"),
            ("quarto", "Quarto"),
            ("tabloid", "Tabloid"),
            ("unspecified", "Unspecified"),
        ]
        return page_size_lst

    def _default_page_layout_type(self):
        page_layout_type_lst = [
            ("0", "選擇Page Layout"),
            ("portrait", "Portrait"),
            ("landscape", "Landscape"),
        ]
        return page_layout_type_lst

    def _all_receiver_name(self):
        query_result = self.env["bi.email.report.receiver.info.setting"].search(
            []
        )
        _select_list = [("0", "請選擇收件者")]
        # For some unknown reason when using qr.dw_oid will give error
        for qr in query_result:
            _select_list.append((qr.name, qr.name))
        return _select_list

    def _all_sending_time(self):
        send_time_choice_lst = [
            ("0", "選擇發送時間"),
            ("0900", "0900"),
            ("0930", "0930"),
            ("1000", "1000"),
            ("1030", "1030"),
            ("1100", "1100"),
            ("1130", "1130"),
            ("1200", "1200"),
            ("1230", "1230"),
            ("1300", "1300"),
            ("1330", "1330"),
            ("1400", "1400"),
            ("1430", "1430"),
            ("1500", "1500"),
            ("1530", "1530"),
            ("1600", "1600"),
            ("1630", "1630"),
            ("1700", "1700"),
            ("1730", "1730"),
            ("1800", "1800"),
            ("1830", "1830"),
            ("1900", "1900"),
            ("1930", "1930"),
        ]

        return send_time_choice_lst

    @api.onchange("frequency_type")
    def onchange_frequency_type(self):
        if self.frequency_type == "daily":
            return {"value": {"sending_frequency": "1"}}
        else:
            return {"value": {"sending_frequency": ""}}

    @api.onchange("sending_frequency")
    def onchange_sending_frequency(self):
        if self.sending_frequency:
            check_number = self.sending_frequency.replace(" ", "")
            if (
                len(re.findall("[a-zA-Z]", check_number)) > 0
                and check_number != ""
            ):
                raise ValidationError(
                    f"{self.sending_frequency} isn't the correct format for frequency."
                )
            check_number_lst = check_number.split(",")
            for number in check_number_lst:
                logging.info(number)
                if number.isdigit():
                    if self.frequency_type == "weekly":
                        if int(number) > 0 and int(number) <= 7:
                            pass
                        else:
                            raise ValidationError(
                                f"{self.sending_frequency} is not within the range of week."
                            )
                    else:
                        if int(number) > 0 and int(number) <= 31:
                            pass
                        else:
                            raise ValidationError(
                                f"{self.sending_frequency} is not within the range of month."
                            )
                else:
                    raise ValidationError(
                        f"{self.sending_frequency} contain non-numeric characters."
                    )

    @api.onchange("end_date")
    def onchange_end_date(self):
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError(f"end_date is smaller than start_date")

    @api.onchange("reciever_email")
    def onchange_email_checker(self):
        email_checker_reg = r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"

        if self.reciever_email:
            email_lst = self.reciever_email.replace(" ", "").split(",")
            for email_info in email_lst:
                if re.match(email_checker_reg, email_info):
                    pass
                else:
                    ValidationError(f"{email_info} is not email format.")
