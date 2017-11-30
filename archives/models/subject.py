# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Subject(models.Model):
    _name = 'archives.subject'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在相同科目"),
    ]

    name = fields.Char(string=u'科目', required=True)

    type_id = fields.Many2one('archives.common_archive', string=u'类型', domain=[('archive_name', '=', 23)])
