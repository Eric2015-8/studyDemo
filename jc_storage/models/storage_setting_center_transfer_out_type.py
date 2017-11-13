# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

create_type = [(1, '不生成'), (10, '未审核'), (20, '已审核')]


class StorageSettingCenterTransferOutType(models.Model):
    _name = 'setting_center.transfer_out_type'
    _description = u'设置：设置中心_仓储_调出类型'

    name = fields.Char(string=u'单据编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: '新建')

    transfer_out_type_id = fields.Many2one('archives.common_archive', string=u'调出类型', required=True,
                                           domain="[('archive_name','=',20)]")
    transfer_out_2_in_type = fields.Selection(create_type, default=10, string=u'调拨出库生成调拨入库方式', required=True)

    def _set_name(self, values):
        values['name'] = self.env['archives.common_archive'].browse(values['transfer_out_type_id']).name

    @api.model
    def create(self, values):
        self._check_not_same_create(values['transfer_out_type_id'])
        self._set_name(values)
        result = super(StorageSettingCenterTransferOutType, self).create(values)
        return result

    def _check_not_same_create(self, transfer_out_type_id):
        count = self.search_count([('transfer_out_type_id', '=', transfer_out_type_id)])
        if count:
            raise ValidationError(u"调出类型类型已设置过")
        return

    def query_type(self, transfer_out_type_id_):
        if not transfer_out_type_id_:
            return None

        result = self.search([('transfer_out_type_id', '=', transfer_out_type_id_)])
        if result:
            return result[0].transfer_out_2_in_type

        return self.env['setting_center'].query_transfer_out_type_2_bill_default()
