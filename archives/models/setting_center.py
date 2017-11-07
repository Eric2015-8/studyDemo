# -*- coding: utf-8 -*-
from odoo import api, fields, models

# create_type = [(1, '不生成'), (10, '未审核'), (20, '已审核')]


class SettingCenter(models.TransientModel):
    _name = 'setting_center'
    _inherit = 'res.config.settings'
    _description = u'设置：设置中心'
