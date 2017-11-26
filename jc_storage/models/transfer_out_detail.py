# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransferOutDetail(models.Model):
    _name = 'jc_storage.transfer_out.detail'
    _description = u'仓储：调拨出库明细'

    _inherit = ['goods.detail']

    transfer_out_id = fields.Many2one('jc_storage.transfer_out', string=u'调拨出库引用', required=True,
                                      ondelete='cascade', index=True, copy=False)

    remark = fields.Char(string=u'备注')
