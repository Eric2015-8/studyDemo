# -*- coding: utf-8 -*-
from odoo import api, fields, models

create_type = [(1, '不生成'), (10, '未审核'), (20, '已审核')]


class StorageSettingCenter(models.TransientModel):
    _name = 'setting_center'
    _inherit = 'setting_center'
    _description = u'设置：设置中心_仓储'

    # 销售流程
    transfer_out_2_in_type_default = fields.Selection(create_type, default=1, readonly=True,
                                                      string=u'调拨出库生成调拨入库方式')

    # 销售出库
    sale_out_store_date_early_today_when_check = fields.Boolean(string=u'审核时，出库日期能早于当前日期')

    @api.model
    def get_default_transfer_out_2_in_type_default(self, fields_):
        data = self.env["ir.config_parameter"].get_param("jc_sale.transfer_out_2_in_type_default", default=10)
        if data:
            data = int(data)
        return {'transfer_out_2_in_type_default': data or 10}

    @api.multi
    def set_transfer_out_2_in_type_default(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("jc_sale.transfer_out_2_in_type_default",
                                                      record.transfer_out_2_in_type_default or 10)

    @api.model
    def get_default_sale_out_store_date_early_today_when_check(self, fields_):
        data = self.env["ir.config_parameter"].get_param("jc_storage.sale_out_store_date_early_today_when_check")
        if data:
            data = bool(data)
        return {'sale_out_store_date_early_today_when_check': data}

    @api.multi
    def set_sale_out_store_date_early_today_when_check(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("jc_storage.sale_out_store_date_early_today_when_check",
                                                      record.sale_out_store_date_early_today_when_check)

    def query_transfer_out_type_2_bill_default(self):
        return self.get_default_transfer_out_2_in_type_default(None)

    def query_date_can_earlier_today(self):
        return self.get_default_sale_out_store_date_early_today_when_check(None)[
            'sale_out_store_date_early_today_when_check']
