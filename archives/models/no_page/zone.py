# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Zone(models.Model):
    _name = 'archives.zone'
    #    _sql_constraints = [
    #        ('name_unique',
    #         'UNIQUE(name)',
    #         "已存在相同地区"),
    #    ]

    name = fields.Char(string=u'地区', required=True)
