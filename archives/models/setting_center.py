# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SettingCenter(models.TransientModel):
    _name = 'setting_center'
    _inherit = 'res.config.settings'
    _description = u'设置中心'
