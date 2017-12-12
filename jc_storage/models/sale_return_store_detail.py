# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.utils import bill_define


class SaleReturnStoreDetail(models.Model):
    _name = 'jc_storage.sale_return_store.detail'
    _description = u'仓储：销售退库-退货信息明细'

    _inherit = ['goods.detail']

    sale_return_store_id = fields.Many2one('jc_storage.sale_return_store', string=u'销售退库引用', required=True,
                                           ondelete='cascade', index=True, copy=False)

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)
    source_detail_id = fields.Integer(string="来源单据明细号", readonly=True, copy=False, default=0)

    remark = fields.Char(string=u'备注')
