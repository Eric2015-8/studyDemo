# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

create_type = [(1, '不生成'), (10, '未审核'), (20, '已审核')]


class SaleSettingCenterSaleType(models.Model):
    _name = 'setting_center.sale_type'
    _description = u'设置：设置中心_销售_销售类型'

    name = fields.Char(string=u'单据编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: '新建')

    type_id = fields.Many2one('archives.common_archive', string=u'销售类型', required=True,
                              domain=[('archive_name', '=', 1)])
    forecast_2_oder_type = fields.Selection(create_type, default=1, string=u'预报生成订单方式', required=True)
    order_2_out_store_type = fields.Selection(create_type, default=10, string=u'订单生成出库方式', required=True)
    out_store_2_account_type = fields.Selection(create_type, default=10, string=u'出库生成账单方式', required=True)
    account_2_invoice_type_default = fields.Selection(create_type, default=10, string=u'账单生成发票方式', required=True)

    def _set_name(self, values):
        values['name'] = self.env['archives.common_archive'].browse(values['type_id']).name

    @api.model
    def create(self, values):
        self._check_not_same_create(values['type_id'])
        self._set_name(values)
        result = super(SaleSettingCenterSaleType, self).create(values)
        return result

    def _check_not_same_create(self, type_id):
        count = self.search_count([('type_id', '=', type_id)])
        if count:
            raise ValidationError(u"销售类型已设置过")
        return

    def query_type(self, type_id_):
        if not type_id_:
            return None

        result = self.search([('type_id', '=', type_id_)])
        if result:
            return result[0].forecast_2_oder_type, \
                   result[0].order_2_out_store_type, \
                   result[0].out_store_2_account_type, \
                   result[0].account_2_invoice_type_default

        return self.env['setting_center'].query_sale_type_2_bill_default()
