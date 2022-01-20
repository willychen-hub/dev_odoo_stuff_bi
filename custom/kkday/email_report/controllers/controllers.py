# -*- coding: utf-8 -*-
# from odoo import http


# class EmailReport(http.Controller):
#     @http.route('/email_report/email_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/email_report/email_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('email_report.listing', {
#             'root': '/email_report/email_report',
#             'objects': http.request.env['email_report.email_report'].search([]),
#         })

#     @http.route('/email_report/email_report/objects/<model("email_report.email_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('email_report.object', {
#             'object': obj
#         })
