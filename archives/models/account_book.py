# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.utils import bill_define
from . import base_infor


class AccountBook(base_infor.BaseInfoUnique):
    _name = 'archives.account_book'
    _description = u'档案：账本'

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())

    detail = fields.One2many('archives.account_book_detail', 'account_book_id',
                             string=u'账本明细', copy=True)
