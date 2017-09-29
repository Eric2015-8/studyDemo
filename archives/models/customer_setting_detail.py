# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CustomerSettingDetail(models.Model):
    _name = 'archives.customer_setting.detail'
    _description = u'档案：个性设置_明细'

    customer_setting_id = fields.Many2one('archives.customer_setting', string=u'个性设置引用', required=True,
                                          ondelete='cascade', index=True, copy=False)

    field = fields.Char(string=u'字段')

    # is_hide = fields.Boolean('是否隐藏')

    value = fields.Integer(string=u"默认值")
