# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

create_type = [(1, '不生成'), (10, '未审核'), (20, '已审核')]


class SaleSettingCenterReturnType(models.Model):
    _name = 'setting_center.return_type'
    _description = u'设置：设置中心_销售_销售退货类型'

    name = fields.Char(string=u'单据编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: '新建')

    sale_return_type_id = fields.Many2one('archives.common_archive', string=u'销售退货类型', required=True,
                                          domain="[('archive_name','=',22)]")
    return_store_2_account_type = fields.Selection(create_type, default=10, string=u'销售退货生成账单方式', required=True)

    def _set_name(self, values):
        values['name'] = self.env['archives.common_archive'].browse(values['sale_return_type_id']).name

    @api.model
    def create(self, values):
        self._check_not_same_create(values['sale_return_type_id'])
        self._set_name(values)
        result = super(SaleSettingCenterReturnType, self).create(values)
        return result

    def _check_not_same_create(self, sale_return_type_id):
        count = self.search_count([('sale_return_type_id', '=', sale_return_type_id)])
        if count:
            raise ValidationError(u"销售退货类型已设置过")
        return

    def query_type(self, sale_return_type_id_):
        if not sale_return_type_id_:
            return None

        result = self.search([('sale_return_type_id', '=', sale_return_type_id_)])
        if result:
            return result[0].return_store_2_account_type

        return self.env['setting_center'].query_return_type_2_bill_default()
