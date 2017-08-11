# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Duty(models.Model):
    _name = 'archives.duty'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名职务"),
    ]

    name = fields.Char(string=u'职务', required=True)
