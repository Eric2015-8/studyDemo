# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleForecast(models.Model):
    _name = 'jc_sale.sale_forecast'
    #    _sql_constraints = [
    #        ('name_unique',
    #         'UNIQUE(name)',
    #         "已存在相同销售预报"),
    #    ]

    # name = fields.Char(string=u'销售预报', required=True, help=u'')
    customer_id=fields.Many2one('archives.customer',string=u'客户名称', required=True)
    date=fields.Date(string=u'日期', required=True,default=fields.Date.today)
    saleType_id=fields.Many2one('archives.sale_type',string=u'销售类型', required=True)
    remark=fields.Char(string=u'摘要')

    #     value = fields.Integer()
    #     value2 = fields.Float(compute="_value_pc", store=True)
    #     description = fields.Text()
    #
    #     @api.depends('value')
    #     def _value_pc(self):
    #         self.value2 = float(self.value) / 100