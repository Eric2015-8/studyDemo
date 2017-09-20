# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Duty(models.Model):
    _name = 'archives.duty'
    _description = u'无菜单档案：职务'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名职务"),
    ]

    name = fields.Char(string=u'职务', required=True)
