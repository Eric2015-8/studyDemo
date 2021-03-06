# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import jc_base


class OutBill(jc_base.Bill):
    _name = 'jc_finance.out_bill'
    _description = u'财务：转出账单'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    @api.model
    def _needaction_domain_get(self):
        return [('bill_state', '=', 1)]

    out_customer_id = fields.Many2one('archives.customer', string=u'转出单位',
                                      domain=lambda self: self.env['archives.organization'].get_customer_organization())
    in_customer_id = fields.Many2one('archives.customer', string=u'转入单位',
                                     domain=lambda self: self.env['archives.organization'].get_customer_organization())
    out_staff_id = fields.Many2one('archives.staff', string=u'转出员工')
    in_staff_id = fields.Many2one('archives.staff', string=u'转入员工')
    type_id = fields.Many2one('archives.common_archive', string=u'转账类型', required=True,
                              domain=[('archive_name', '=', 29)])

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    detail = fields.One2many('jc_finance.out_bill_detail', 'out_bill_id', string=u'转出账单明细', copy=True)

    @api.model
    def get_code(self):
        return self._name

    def do_customer_setting(self):
        table_show_name = u'转出账单'
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(OutBill, self).default_get(fields_)
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res


need_set_fields = ['company_id', 'department_id']
