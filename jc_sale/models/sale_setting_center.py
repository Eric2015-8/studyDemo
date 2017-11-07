# -*- coding: utf-8 -*-
from odoo import api, fields, models

create_type = [(1, '不生成'), (10, '未审核'), (20, '已审核')]


class SaleSettingCenter(models.TransientModel):
    _name = 'setting_center'
    _inherit = 'setting_center'
    _description = u'设置：设置中心_销售'

    forecast_2_oder_type_default = fields.Selection(create_type, default=1, readonly=True,
                                                    string=u'预报生成订单方式')
    order_2_out_store_type_default = fields.Selection(create_type, default=10, readonly=True,
                                                      string=u'订单生成出库方式')
    out_store_2_account_type_default = fields.Selection(create_type, default=10, readonly=True,
                                                        string=u'出库生成账单方式')
