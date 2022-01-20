# -*- coding: utf-8 -*-
from odoo import api, fields, models


# This is to create a the column for later usage.
class ShowUserPage(models.Model):
    _name = "er.show_user_setting"
    _description = "The list page of email setting"

    name = fields.Char("Reciever Name", required=True)
    default_email = fields.Text(size=150)

    # Checkbox
    service_list = fields.Many2many(
        "service", string="Services List"
    )

    current_user_email = fields.Text(
        size=150,
        default=lambda self: self.get_current_user_email(),
        readonly=True,
    )

    def get_current_user_email(self):
        """
        Getting the current login user's email

        Returns:
            String: The current login user's email.
        """
        return self.env.user.email

    def wiz_change_user_setting(self):
        """
        Change user's default name on the page

        Returns:
            dict: The information of the wizard
        """
        return {
            "type": "ir.actions.act_window",
            "res_model": "email_report.user.update.wizard",
            "view_mode": "form",
            "target": "new",
        }


class Services(models.Model):
    _name = "service"

    name = fields.Char("Services")
