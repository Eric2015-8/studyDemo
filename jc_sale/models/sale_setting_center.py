# -*- coding: utf-8 -*-
from odoo import api, fields, models

create_type = [(1, '不生成'), (10, '未审核'), (20, '已审核')]


class SaleSettingCenter(models.TransientModel):
    _name = 'setting_center'
    _inherit = 'setting_center'
    _description = u'设置：设置中心_销售'

    # 销售流程
    forecast_2_oder_type_default = fields.Selection(create_type, default=1, readonly=True,
                                                    string=u'预报生成订单方式')
    order_2_out_store_type_default = fields.Selection(create_type, default=10, readonly=True,
                                                      string=u'订单生成出库方式')
    out_store_2_account_type_default = fields.Selection(create_type, default=10, readonly=True,
                                                        string=u'出库生成账单方式')
    account_2_invoice_type_default = fields.Selection(create_type, default=10, readonly=True,
                                                      string=u'账单生成发票方式')

    # 销售退货流程
    sale_return_2_return_store_type_default = fields.Selection(create_type, default=10, readonly=True,
                                                               string=u'销售退单生成销售退货方式')
    return_store_2_account_type_default = fields.Selection(create_type, default=10, readonly=True,
                                                           string=u'销售退货生成账单方式')
    account_2_invoice_return_type_default = fields.Selection(create_type, default=10, readonly=True,
                                                             string=u'账单生成发票方式')

    @api.model
    def get_default_forecast_2_oder_type_default(self, fields_):
        data = self.env["ir.config_parameter"].get_param("jc_sale.forecast_2_oder_type_default", default=1)
        if data:
            data = int(data)
        return {'forecast_2_oder_type_default': data or 1}

    @api.multi
    def set_forecast_2_oder_type_default(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("jc_sale.forecast_2_oder_type_default",
                                                      record.forecast_2_oder_type_default or 1)

    @api.model
    def get_default_order_2_out_store_type_default(self, fields_):
        data = self.env["ir.config_parameter"].get_param("jc_sale.order_2_out_store_type_default", default=10)
        if data:
            data = int(data)
        return {'order_2_out_store_type_default': data or 10}

    @api.multi
    def set_order_2_out_store_type_default(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("jc_sale.order_2_out_store_type_default",
                                                      record.order_2_out_store_type_default or 10)

    @api.model
    def get_default_out_store_2_account_type_default(self, fields_):
        data = self.env["ir.config_parameter"].get_param("jc_sale.out_store_2_account_type_default", default=10)
        if data:
            data = int(data)
        return {'out_store_2_account_type_default': data or 10}

    @api.multi
    def set_out_store_2_account_type_default(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("jc_sale.out_store_2_account_type_default",
                                                      record.out_store_2_account_type_default or 10)

    @api.model
    def get_default_account_2_invoice_type_default(self, fields_):
        data = self.env["ir.config_parameter"].get_param("jc_sale.account_2_invoice_type_default", default=10)
        if data:
            data = int(data)
        return {'account_2_invoice_type_default': data or 10}

    @api.multi
    def set_account_2_invoice_type_default(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("jc_sale.account_2_invoice_type_default",
                                                      record.account_2_invoice_type_default or 10)

    @api.model
    def get_default_sale_return_2_return_store_type_default(self, fields_):
        data = self.env["ir.config_parameter"].get_param("jc_sale.sale_return_2_return_store_type_default", default=10)
        if data:
            data = int(data)
        return {'sale_return_2_return_store_type_default': data or 10}

    @api.multi
    def set_sale_return_2_return_store_type_default(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("jc_sale.sale_return_2_return_store_type_default",
                                                      record.sale_return_2_return_store_type_default or 10)

    @api.model
    def get_default_return_store_2_account_type_default(self, fields_):
        data = self.env["ir.config_parameter"].get_param("jc_sale.return_store_2_account_type_default", default=10)
        if data:
            data = int(data)
        return {'return_store_2_account_type_default': data or 10}

    @api.multi
    def set_return_store_2_account_type_default(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("jc_sale.return_store_2_account_type_default",
                                                      record.return_store_2_account_type_default or 10)

    @api.model
    def get_default_account_2_invoice_return_type_default(self, fields_):
        data = self.env["ir.config_parameter"].get_param("jc_sale.account_2_invoice_return_type_default", default=10)
        if data:
            data = int(data)
        return {'account_2_invoice_return_type_default': data or 10}

    @api.multi
    def set_account_2_invoice_return_type_default(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("jc_sale.account_2_invoice_return_type_default",
                                                      record.account_2_invoice_return_type_default or 10)

    def query_sale_type_2_bill_default(self):
        a = self.get_default_forecast_2_oder_type_default(None)
        b = self.get_default_order_2_out_store_type_default(None)
        c = self.get_default_out_store_2_account_type_default(None)
        d = self.get_default_account_2_invoice_type_default(None)
        return a, b, c, d

    def query_return_type_2_bill_default(self):
        return self.get_default_sale_return_2_return_store_type_default(None), \
               self.get_default_return_store_2_account_type_default(None), \
               self.get_default_account_2_invoice_return_type_default(None)
