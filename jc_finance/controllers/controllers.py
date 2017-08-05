# -*- coding: utf-8 -*-
from odoo import http

# class JcFinance(http.Controller):
#     @http.route('/jc_finance/jc_finance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jc_finance/jc_finance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('jc_finance.listing', {
#             'root': '/jc_finance/jc_finance',
#             'objects': http.request.env['jc_finance.jc_finance'].search([]),
#         })

#     @http.route('/jc_finance/jc_finance/objects/<model("jc_finance.jc_finance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jc_finance.object', {
#             'object': obj
#         })