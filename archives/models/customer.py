# -*- coding: utf-8 -*-

from odoo import models, fields, api
from . import utils


# import sys;
#
# sys.path.append("..");
# import utils


class Customer(models.Model):
    _name = 'archives.customer'
    _description = u'档案：客户'

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名客户"),
    ]

    name = fields.Char(string=u'客户', required=True)
    short_name = fields.Char(string=u'简称')
    spell = fields.Char(string=u'首拼')

    # 通用信息
    tel = fields.Char(string=u'联系方式')
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True)
    address = fields.Char(string=u'地址')
    zone_id = fields.Many2one('archives.zone', string=u'地址')
    zone_type1_id = fields.Many2one('archives.zone_type1', string=u'地区分类1', store=True, compute='_set_zone_type')
    zone_type2_id = fields.Many2one('archives.zone_type2', string=u'地区分类2', store=True, compute='_set_zone_type')
    company_id = fields.Many2one('res.company', string=u'公司', index=True)
    price_type_id = fields.Many2one('archives.common_archive', string=u'价格分类', domain="[('archive_name','=',19)]")

    # 地址 & 联系人

    # 客户分类
    customer_type_id = fields.Many2one('archives.common_archive', string=u'客户分类')
    customer_type1_id = fields.Many2one('archives.common_archive', string=u'客户分类1')
    customer_type2_id = fields.Many2one('archives.common_archive', string=u'客户分类2')
    customer_type3_id = fields.Many2one('archives.common_archive', string=u'客户分类3')
    customer_type4_id = fields.Many2one('archives.common_archive', string=u'客户分类4')
    customer_type5_id = fields.Many2one('archives.common_archive', string=u'客户分类5')
    customer_type6_id = fields.Many2one('archives.common_archive', string=u'客户分类6')

    # 权限
    organization_id = fields.Many2one('archives.common_archive', string=u'客户权限', domain="[('archive_name','=',16)]")

    #     value = fields.Integer()
    #     value2 = fields.Float(compute="_value_pc", store=True)
    #     description = fields.Text()
    #
    #     @api.depends('value')
    #     def _value_pc(self):
    #         self.value2 = float(self.value) / 100

    @api.depends('zone_id')
    def _set_zone_type(self):
        for record in self:
            record.zone_type1_id = record.zone_id.zone_type1_id
            record.zone_type2_id = record.zone_id.zone_type2_id
        return

    @api.model
    def create(self, values):
        utils.set_spell(values)
        return super(Customer, self).create(values)

    @api.multi
    def write(self, values):
        utils.set_spell(values)
        return super(Customer, self).write(values)

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Customer, self).copy(default)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # if operator not in ('ilike', 'like', '=', '=like', '=ilike'):
        #     return super(Customer, self).name_search(name, args, operator, limit)
        args = args or []
        domain = ['|', ('spell', operator, name), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
