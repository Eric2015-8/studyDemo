# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Bank(models.Model):
    _name = 'archives.bank'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在相同银行"),
    ]

    name = fields.Char(string=u'银行', required=True)
