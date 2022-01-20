# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models


# This is to create a the column for later usage.
class ShowEmailPage(models.Model):
    _name = "er.show_email_setting"
    _description = "The list page of email setting"

    @api.model
    def _get_data(self):
        query_result = self.env["er.show_user_setting"].search([])
        _select_list = [("1", "請選擇收件者")]
        for qr in query_result:
            _select_list.append((qr.name, qr.name))
        return _select_list

    @api.model
    def _get_select_lst(self):
        select_lst = self._get_data()
        return select_lst

    name = fields.Selection(
        selection="_get_select_lst",
        required=True,
        default="1",
    )

    email = fields.Text("Reciever Email", compute='_compute_email')

    @api.depends('name')
    def _compute_email(self):
        pass


    subject = fields.Text("Email Subject", size=150)
    content = fields.Text("Email Content", size=500)
    file_name = fields.Text("File Name", size=500)
    file_link = fields.Text("File Link", size=500)
    sending_time = fields.Text("Sending Time", size=500)
    frequency_type = fields.Text("Freqyuency Type", size=500)
    start_date = fields.Datetime("Start date")
    end_date = fields.Datetime("End date")
    export_status_flag = fields.Boolean("Export Flag", size=500)
