# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import bill_define
from . import jc_base


class Receipt(jc_base.Bill):
    _name = 'jc_finance.receipt'
    _description = u'财务：收款单'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    # source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    # source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)

    customer_id = fields.Many2one('archives.customer', string=u'收款单位',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())

    account_id = fields.Many2one('archives.account', string=u'账户', required=True)
    staff_id = fields.Many2one('archives.staff', string=u'员工')
    type_id = fields.Many2one('archives.common_archive', string=u'收款类型', domain=[('archive_name', '=', 24)])

    detail = fields.One2many('jc_finance.receipt_detail', 'receipt_id',
                             string=u'销售账单明细', copy=True)

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    @api.model
    def get_code(self):
        return self._name

    # @api.onchange('customer_id')
    # def _onchange_for_staff(self):
    #     self.staff_id = self.customer_id.staff_id

    @api.model
    def _needaction_domain_get(self):
        return [('bill_state', '=', 1)]

    def do_customer_setting(self):
        table_show_name = u'收款单'
        need_set_fields = ['customer_id', 'company_id', 'staff_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(Receipt, self).default_get(fields_)
        need_set_fields = ['customer_id', 'company_id', 'staff_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res
