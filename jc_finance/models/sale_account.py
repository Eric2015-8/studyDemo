# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import bill_define
from . import jc_base


class SaleAccount(jc_base.Bill):
    _name = 'jc_finance.sale_account'
    _description = u'财务：销售账单'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)

    order_name = fields.Char(string=u'订单号', readonly=True)

    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())

    type_id = fields.Many2one('archives.common_archive', string=u'销售类型', domain=[('archive_name', '=', 1)])

    sale_account_detail = fields.One2many('jc_finance.sale_account.detail', 'sale_account_id',
                                          string=u'销售账单明细', copy=True)

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True, domain=[('is_sale_man', '=', True)])
    store_id = fields.Many2one('archives.store', string=u'仓库',
                               domain=lambda self: self.env['archives.organization'].get_store_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())
    out_store_date = fields.Date(string=u'出库日期', required=True, default=fields.Date.today)

    total_second_number = fields.Float(string='辅数量', store=True, readonly=True, compute='_amount_all',
                                       track_visibility='always')
    total_main_number = fields.Float(string='主数量', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    total_money = fields.Float(string='金额', store=True, readonly=True, compute='_amount_all', track_visibility='always')

    @api.model
    def get_code(self):
        return self._name

    @api.depends('sale_account_detail.second_unit_number', 'sale_account_detail.main_unit_number',
                 'sale_account_detail.money')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            total_second = 0.0
            total_main = 0.0
            total_money = 0.0
            for line in order.sale_account_detail:
                total_second += line.second_unit_number
                total_main += line.main_unit_number
                total_money += line.money
            order.update({
                'total_second_number': total_second,
                'total_main_number': total_main,
                'total_money': total_money,
            })

    @api.onchange('customer_id')
    def _onchange_for_staff(self):
        self.staff_id = self.customer_id.staff_id

    @api.model
    def _needaction_domain_get(self):
        return [('bill_state', '=', 1)]

    @api.multi
    def do_customer_setting(self):
        table_show_name = u'销售账单'
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(SaleAccount, self).default_get(fields_)
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res
