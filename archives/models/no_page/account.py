# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Account(models.Model):
    _name = 'archives.account'
    #    _sql_constraints = [
    #        ('name_unique',
    #         'UNIQUE(name)',
    #         "已存在相同账号"),
    #    ]

    name = fields.Char(string=u'账号', required=True)