# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Customer(models.Model):
    _name = 'archives.customer'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名客户"),
    ]

    name = fields.Char(string=u'客户名称', required=True)
    short_name = fields.Char(string=u'简称')

    # 通用信息
    tel = fields.Char(string=u'联系方式')
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True)
    address = fields.Char(string=u'地址')
    zone_id = fields.Many2one('archives.zone', string=u'地址')
    zone_type1_id = fields.Many2one('archives.zone_type1', string=u'地区分类1')
    zone_type2_id = fields.Many2one('archives.zone_type2', string=u'地区分类2')
    company_id = fields.Many2one('res.company', string=u'公司', index=True)

    # 地址 & 联系人

    # 客户分类
    customer_type_id = fields.Many2one('archives.customer_type', string=u'客户分类')
    customer_type1_id = fields.Many2one('archives.customer_type1', string=u'客户分类1')
    customer_type2_id = fields.Many2one('archives.customer_type2', string=u'客户分类2')
    customer_type3_id = fields.Many2one('archives.customer_type3', string=u'客户分类3')
    customer_type4_id = fields.Many2one('archives.customer_type4', string=u'客户分类4')
    customer_type5_id = fields.Many2one('archives.customer_type5', string=u'客户分类5')
    customer_type6_id = fields.Many2one('archives.customer_type6', string=u'客户分类6')
    #     value = fields.Integer()
    #     value2 = fields.Float(compute="_value_pc", store=True)
    #     description = fields.Text()
    #
    #     @api.depends('value')
    #     def _value_pc(self):
    #         self.value2 = float(self.value) / 100
