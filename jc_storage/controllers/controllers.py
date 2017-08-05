# -*- coding: utf-8 -*-
from odoo import http

# class JcStorage(http.Controller):
#     @http.route('/jc_storage/jc_storage/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jc_storage/jc_storage/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('jc_storage.listing', {
#             'root': '/jc_storage/jc_storage',
#             'objects': http.request.env['jc_storage.jc_storage'].search([]),
#         })

#     @http.route('/jc_storage/jc_storage/objects/<model("jc_storage.jc_storage"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jc_storage.object', {
#             'object': obj
#         })