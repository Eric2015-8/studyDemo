# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import bill_define
from . import jc_base
import datetime


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

    @api.multi
    def print_quotation(self):
        if self.bill_state < 10:
            raise ValidationError('审核后才能打印')
        return self.env['report'].get_action(self, 'jc_finance.report_pdf_sale_account')

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
    def do_check(self):
        self._check_logic()
        super(SaleAccount, self).do_check()

    @api.multi
    def do_un_check(self):
        self._delete_sale_invoice()
        super(SaleAccount, self).do_un_check()

    def _delete_sale_invoice(self):
        bills = self.env["jc_finance.sale_invoice"].search(
            [('source_bill_id', '=', self.id), ('source_bill_type', '=', 40)])
        if bills:
            for bill in bills:
                bill.unlink()

    def _check_logic(self):
        if not self.type_id:
            raise ValidationError(u'未选择{销售类型}')
        module = 'setting_center.sale_type'
        index = 3
        info = '销售流程'
        if self.source_bill_type == 23:
            module = 'setting_center.return_type'
            index = 2
            info = '退货流程'
        setting = self.env[module].query_type(self.type_id.id)
        if not setting:
            raise ValidationError(u'请到【设置中心】“销售”下设置“{}”！'.format(info))
        _type = setting[index]
        if _type == 1:
            return
        bill = self._create_sale_invoice()
        if _type == 20:
            bill.do_check()
        return

    def _create_sale_invoice(self):
        _type_id = self._query_type_id()
        if not _type_id:
            raise ValidationError(u'没有{发票类型}，请到 档案 - 通用档案 中添加{档案名称}为“销售发票”的档案')
        values = self._get_bill_values(_type_id)
        bill = self.env['jc_finance.sale_invoice'].create(values)
        for detail in self.sale_account_detail:
            bill_values = self._get_detail_values_bill(bill, detail)
            self.env['jc_finance.sale_invoice_bill_detail'].create(bill_values)
            invoice_values = self._get_detail_values_invoice(bill, detail)
            self.env['jc_finance.sale_invoice_invoice_detail'].create(invoice_values)
        return bill

    def _query_type_id(self):  # 取第一个发票类型
        return self.env['archives.common_archive'].search([('archive_name', '=', 27)], limit=1, order='id').id

    def _get_bill_values(self, _type_id):
        values = {
            'source_bill_id': self.id,
            'source_bill_type': 40,  # 销售账单
            'order_name': self.order_name,
            'customer_id': self.customer_id.id,
            'date': datetime.datetime.today(),
            'type_id': _type_id,
            'company_id': self.company_id.id,
            'department_id': self.department_id.id,
            'invoice_customer': self.customer_id.name,
            'staff_id': self.staff_id.id,
            'remark': self.remark,
            # 'total_main_number': self.total_main_number,
            # 'total_second_number': self.total_second_number,
            # 'total_money': self.total_money,
        }
        return values

    def _get_detail_values_bill(self, bill, detail):
        values = {
            'sale_invoice_id': bill.id,
            'source_bill_type': 40,  # 销售账单
            'source_bill_id': self.id,
            'source_detail_id': detail.id,
            'order_name': self.order_name,
            'bill_type_id': 40,  # 销售账单
            'date': bill.date,
            'goods_id': detail.goods_id.id,
            'main_unit_number': detail.main_unit_number,
            'price': detail.price,
            'money': detail.money,
            'remark': detail.remark,
        }
        return values

    def _get_detail_values_invoice(self, bill, detail):
        values = {
            'sale_invoice_id': bill.id,
            'goods_id': detail.goods_id.id,
            'goods_invoice': detail.goods_id.name,
            'main_unit_id': detail.main_unit_id.id,
            'number': detail.main_unit_number,
            'price': detail.price,
            'money': detail.money,
            'remark': detail.remark,
        }
        return values

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
