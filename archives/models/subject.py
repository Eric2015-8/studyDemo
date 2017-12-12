# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import base_infor


class Subject(base_infor.BaseInfoUnique):
    _name = 'archives.subject'

    name = fields.Char(string=u'科目', required=True)

    type_id = fields.Many2one('archives.common_archive', string=u'类型', domain=[('archive_name', '=', 23)])
