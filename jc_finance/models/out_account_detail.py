# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OutAccountDetail(models.Model):
    _name = 'jc_finance.out_account_detail'
    _description = u'财务：转出款单明细'

    out_account_id = fields.Many2one('jc_finance.out_account', string=u'转出款单引用', required=True,
                                     ondelete='cascade', index=True, copy=False)

    subject_id = fields.Many2one('archives.subject', string=u'科目', required=True)
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额', store=True)
    remark = fields.Char(string=u'备注')
