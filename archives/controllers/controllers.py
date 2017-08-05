# -*- coding: utf-8 -*-
from odoo import http

# class Archives(http.Controller):
#     @http.route('/archives/archives/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/archives/archives/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('archives.listing', {
#             'root': '/archives/archives',
#             'objects': http.request.env['archives.archives'].search([]),
#         })

#     @http.route('/archives/archives/objects/<model("archives.archives"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('archives.object', {
#             'object': obj
#         })