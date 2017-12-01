# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import jc_base


class MemoTicket(jc_base.Bill):
    _name = 'jc_finance.memo_ticket'
    _description = u'财务：记账单'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    customer_id = fields.Many2one('archives.customer', string=u'往来单位',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())

    staff_id = fields.Many2one('archives.staff', string=u'员工')
    type_id = fields.Many2one('archives.common_archive', string=u'记账类型', domain=[('archive_name', '=', 26)])

    detail = fields.One2many('jc_finance.memo_ticket_detail', 'memo_ticket_id',
                             string=u'记账单明细', copy=True)

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    @api.model
    def get_code(self):
        return self._name

    @api.model
    def _needaction_domain_get(self):
        return [('bill_state', '=', 1)]

    @api.multi
    def do_customer_setting(self):
        table_show_name = u'记账单'
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(MemoTicket, self).default_get(fields_)
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res


need_set_fields = ['customer_id', 'company_id', 'staff_id',  'department_id']
