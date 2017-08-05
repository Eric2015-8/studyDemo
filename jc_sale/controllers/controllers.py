# -*- coding: utf-8 -*-
from odoo import http

# class JcSale(http.Controller):
#     @http.route('/jc_sale/jc_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jc_sale/jc_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('jc_sale.listing', {
#             'root': '/jc_sale/jc_sale',
#             'objects': http.request.env['jc_sale.jc_sale'].search([]),
#         })

#     @http.route('/jc_sale/jc_sale/objects/<model("jc_sale.jc_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jc_sale.object', {
#             'object': obj
#         })