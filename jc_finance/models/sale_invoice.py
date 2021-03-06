# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import jc_base
from odoo.utils import bill_define, big_number


class SaleInvoice(jc_base.Bill):
    _name = 'jc_finance.sale_invoice'
    _description = u'财务：销售发票'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    @api.model
    def _needaction_domain_get(self):
        return [('bill_state', '=', 1)]

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)

    order_name = fields.Char(string=u'订单号', readonly=True)

    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    type_id = fields.Many2one('archives.common_archive', string=u'发票类型', required=True,
                              domain=[('archive_name', '=', 27)])

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())
    invoice_customer = fields.Char(string=u'开票客户')
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True, domain=[('is_sale_man', '=', True)])

    bill_detail = fields.One2many('jc_finance.sale_invoice_bill_detail', 'sale_invoice_id',
                                  string=u'销售发票_单据明细', copy=True)
    invoice_detail = fields.One2many('jc_finance.sale_invoice_invoice_detail', 'sale_invoice_id',
                                     string=u'销售发票_发票明细', copy=True)

    total_money = fields.Float(string=u'金额', store=True, readonly=True, compute='_amount_all',
                               track_visibility='always')
    total_money_chn = fields.Char(string=u'大写金额', store=True, readonly=True, compute='_amount_all')
    current_user_name = fields.Char(string=u'当前用户', store=False, readonly=True, compute='_get_current_user_name',
                                    track_visibility='always')

    @api.model
    def get_code(self):
        return self._name

    @api.multi
    def print_quotation(self):
        if self.bill_state < 10:
            raise ValidationError('审核后才能打印')
        return self.env['report'].get_action(self, 'jc_finance.report_pdf_sale_invoice')

    @api.depends('invoice_detail.money')
    def _amount_all(self):
        for bill in self:
            total_money = 0.0
            for line in bill.invoice_detail:
                total_money += line.money
            cn = big_number.cn_currency(total_money)
            bill.update({
                'total_money': total_money,
                'total_money_chn': cn,
            })

    @api.depends('invoice_detail.money')
    def _get_current_user_name(self):
        for bill in self:
            bill.current_user_name = self.env['res.users'].browse(self._uid).name

    @api.onchange('customer_id')
    def _onchange_for_staff(self):
        self.invoice_customer = self.customer_id.name

    def do_customer_setting(self):
        table_show_name = u'销售发票'
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(SaleInvoice, self).default_get(fields_)
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res


need_set_fields = ['customer_id', 'company_id', 'department_id']
