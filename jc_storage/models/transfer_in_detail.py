# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from . import bill_define


class TransferInDetail(models.Model):
    _name = 'jc_storage.transfer_in.detail'
    _description = u'仓储：调拨入库明细'

    _inherit = ['goods.detail']

    transfer_in_id = fields.Many2one('jc_storage.transfer_in', string=u'调拨入库引用', required=True,
                                     ondelete='cascade', index=True, copy=False)

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)
    source_detail_id = fields.Integer(string="来源单据明细号", readonly=True, copy=False, default=0)

    remark = fields.Char(string=u'备注')
