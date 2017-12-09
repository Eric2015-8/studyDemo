# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import bill_define
from . import jc_base
import datetime


class SaleOutStore(jc_base.Bill):
    _name = 'jc_storage.sale_out_store'
    _description = u'仓储：销售出库'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)

    order_name = fields.Char(string=u'订单号', readonly=True)

    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())

    type_id = fields.Many2one('archives.common_archive', string=u'销售类型', required=True,
                              domain=[('archive_name', '=', 1)])

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True, domain=[('is_sale_man', '=', True)])
    store_id = fields.Many2one('archives.store', string=u'仓库', required=True,
                               domain=lambda self: self.env['archives.organization'].get_store_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())
    out_store_date = fields.Date(string=u'出库日期', required=True, default=fields.Date.today)
    address = fields.Char(string=u'地址', compute='_compute_address', store=True)

    total_second_number = fields.Float(string='辅数量', store=True, readonly=True, compute='_amount_all',
                                       track_visibility='always')
    total_main_number = fields.Float(string='主数量', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    total_money = fields.Float(string='金额', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    total_money2 = fields.Float(string='金额', related='total_money')

    sale_out_store_detail = fields.One2many('jc_storage.sale_out_store.detail', 'sale_out_store_id', string=u'销售出库订货明细',
                                            copy=True)
    sale_out_store_out_detail = fields.One2many('jc_storage.sale_out_store.out_detail', 'sale_out_store_id',
                                                string=u'销售出库-出库明细', copy=True)

    @api.model
    def get_code(self):
        return self._name

    @api.multi
    def print_quotation(self):
        if self.bill_state < 10:
            raise ValidationError('审核后才能打印')
        return self.env['report'].get_action(self, 'jc_storage.report_pdf_sale_out_store')

    @api.depends('customer_id')
    def _compute_address(self):
        for order in self:
            order.address = order.customer_id.zone_type2_id.name + ' ' + order.customer_id.zone_type1_id.name + ' ' \
                            + order.customer_id.zone_id.name + ' ' + order.customer_id.address

    @api.depends('sale_out_store_detail.second_unit_number', 'sale_out_store_detail.main_unit_number',
                 'sale_out_store_detail.money')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for bill in self:
            total_second = 0.0
            total_main = 0.0
            total_money = 0.0
            for line in bill.sale_out_store_detail:
                total_second += line.second_unit_number
                total_main += line.main_unit_number
                total_money += line.money
            bill.update({
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
    def write(self, values):
        result = super(SaleOutStore, self).write(values)
        self._set_oder_detail()
        return result

    def _set_oder_detail(self):
        for detail in self.sale_out_store_detail:
            detail.main_unit_number = 0
            detail.second_unit_number = 0
            detail.price = 0
            detail.money = 0
            for out_detail in self.sale_out_store_out_detail:
                if out_detail.goods_id == detail.goods_id:
                    detail.main_unit_number += out_detail.main_unit_number
                    detail.second_unit_number += out_detail.second_unit_number
                    detail.money += out_detail.money
            if detail.main_unit_number != 0:
                detail.price = detail.money / detail.main_unit_number
        return

    def _create_sale_account(self):
        values = {
            'source_bill_id': self.id,
            'source_bill_type': 20,  # 销售出库
            'order_name': self.order_name,
            'customer_id': self.customer_id.id,
            'date': datetime.datetime.today(),
            'out_store_date': self.out_store_date,
            'type_id': self.type_id.id,
            'staff_id': self.staff_id.id,
            'department_id': self.department_id.id,
            'store_id': self.store_id.id,
            'company_id': self.company_id.id,
            'remark': self.remark,
            'total_main_number': self.total_main_number,
            'total_second_number': self.total_second_number,
            'total_money': self.total_money,
        }
        bill = self.env['jc_finance.sale_account'].create(values)
        order_number_dic = self._get_order_number_dic()
        for detail in self.sale_out_store_detail:
            values = {
                'sale_account_id': bill.id,
                'source_bill_type': 20,  # 销售出库
                'source_bill_id': self.id,
                'source_detail_id': detail.id,
                'goods_id': detail.goods_id.id,
                'second_unit_id': detail.second_unit_id.id,
                'second_unit_number': detail.second_unit_number,
                'second_unit_number_tmp': detail.second_unit_number_tmp,
                'main_unit_id': detail.main_unit_id.id,
                'main_unit_number': detail.main_unit_number,
                'main_unit_number_tmp': detail.main_unit_number_tmp,
                'price': detail.price,
                'price_tmp': detail.price_tmp,
                'money': detail.money,
                'remark': detail.remark,
            }
            if detail.source_detail_id in order_number_dic:
                values['order_number'] = order_number_dic[detail.source_detail_id]
                values['diff_number'] = order_number_dic[detail.source_detail_id] - detail.main_unit_number
            else:  # 这种情况不应出现。因为整个流程中，相关明细是一一对应的
                values['order_number'] = 0
                values['diff_number'] = 0 - detail.main_unit_number
            self.env['jc_finance.sale_account.detail'].create(values)
        return bill

    def _get_order_number_dic(self):
        dic = {}
        order = self.env['jc_sale.sale_order'].browse(self.source_bill_id)
        for detail in self.sale_out_store_detail:
            for d_order in order.sale_order_detail:
                if d_order.id == detail.source_detail_id:
                    dic[detail.source_detail_id] = d_order.main_unit_number
                    break
        return dic

    def _delete_sale_account(self):
        bills = self.env["jc_finance.sale_account"].search(
            [('source_bill_id', '=', self.id), ('source_bill_type', '=', 20)])
        if bills:
            for bill in bills:
                bill.unlink()

    def _check_logic(self):
        if not self.type_id:
            raise ValidationError(u'未选择{销售类型}')
        self._check_date()
        setting = self.env['setting_center.sale_type'].query_type(self.type_id.id)
        if not setting:
            raise ValidationError(u'请到【设置中心】“销售”下设置“销售流程”！')
        _type = setting[2]
        if _type == 1:
            return
        bill = self._create_sale_account()
        if _type == 20:
            bill.do_check()
        return

    def _check_date(self):
        if datetime.datetime.strptime(self.out_store_date, '%Y-%m-%d').date() < datetime.date.today():
            can_early = self.env['setting_center'].query_date_can_earlier_today()
            if not can_early:
                raise ValidationError('{出库日期}不能早于当前日期')

    @api.multi
    def do_check(self):
        self._check_logic()
        super(SaleOutStore, self).do_check()

    @api.multi
    def do_un_check(self):
        self._delete_sale_account()
        super(SaleOutStore, self).do_un_check()

    @api.multi
    def do_customer_setting(self):
        table = u'jc_storage.sale_out_store'
        table_show_name = u'销售出库'
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(SaleOutStore, self).default_get(fields_)
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res
