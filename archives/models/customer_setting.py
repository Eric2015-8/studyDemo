# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CustomerSetting(models.Model):
    _name = 'archives.customer_setting'
    _description = u'档案：个性设置'

    # _sql_constraints = [
    #     ('name_unique',
    #      'UNIQUE(user_id)',
    #      "已为该用户授权"),
    # ]

    # name = fields.Char(string=u'数据权限名称', required=True, copy=False, readonly=True,
    #                    index=True, default=lambda self: _('新建'))  # 使用用户名

    user_id = fields.Many2one('res.users', string=u'用户', required=True, ondelete='cascade')

    table = fields.Char(string=u'表名', index=True)

    table_name = fields.Char(string=u'表名')

    customer_setting_detail = fields.One2many('archives.customer_setting.detail', 'customer_setting_id',
                                              string=u'个性设置明细', copy=True)
