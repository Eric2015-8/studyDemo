# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import utils

class Store(models.Model):
    _name = 'archives.store'
    _description = u'档案：仓库'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名仓库"),
    ]

    name = fields.Char(string=u'仓库名称',required=True)
    short_name=fields.Char(string=u'简称',help=u'用于报表显示')
    spell = fields.Char(string=u'首拼')

    company_id = fields.Many2one('res.company', string=u'公司', index=True)
    address=fields.Char(string=u'仓库地址')

    @api.model
    def create(self, values):
        utils.set_spell(values)
        return super(Store, self).create(values)

    @api.multi
    def write(self, values):
        utils.set_spell(values)
        return super(Store, self).write(values)
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100