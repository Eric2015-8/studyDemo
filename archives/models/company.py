# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Company(models.Model):
    _name = 'archives.company'
#    _sql_constraints = [
#        ('name_unique',
#         'UNIQUE(name)',
#         "已存在相同公司"),
#    ]

    name = fields.Char(string=u'公司名称',required=True,help=u'您所在的公司的全称')
    shortName=fields.Char(string=u'简称',help=u'用于报表显示')

    staff_ids=fields.One2many('archives.staff','company_id',strig=u'员工')
    store_ids=fields.One2many('archives.store','company_id',string=u'仓库')
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100