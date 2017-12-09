# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from . import bill_define
from . import jc_base


class SaleOrder(jc_base.Bill):
    _name = 'jc_sale.sale_order'
    _description = u'销售：销售订单'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin', 'jc_approve']

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)

    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())

    type_id = fields.Many2one('archives.common_archive', string=u'销售类型', required=True,
                              domain=[('archive_name', '=', 1)])

    sale_order_detail = fields.One2many('jc_sale.sale_order.detail', 'sale_order_id', string=u'销售订单明细', copy=True)

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True, domain="[('is_sale_man','=',True)]")
    store_id = fields.Many2one('archives.store', string=u'仓库',
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

    @api.model
    def get_code(self):
        return self._name

    @api.multi
    def print_quotation(self):
        # self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        if self.bill_state < 10:
            raise ValidationError('审核后才能打印')
        return self.env['report'].get_action(self, 'jc_sale.report_pdf_sale_order')

    @api.depends('customer_id')
    def _compute_address(self):
        for order in self:
            order.address = order.customer_id.zone_type2_id.name + ' ' + order.customer_id.zone_type1_id.name + ' ' \
                            + order.customer_id.zone_id.name + ' ' + order.customer_id.address

    @api.depends('sale_order_detail.second_unit_number', 'sale_order_detail.main_unit_number',
                 'sale_order_detail.money')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            total_second = 0.0
            total_main = 0.0
            total_money = 0.0
            for line in order.sale_order_detail:
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

    def _create_out_store(self):
        values = self._get_bill_values()
        bill = self.env['jc_storage.sale_out_store'].create(values)
        for detail in self.sale_order_detail:
            main, second, price = SaleOrder.get_str_tuple_from_number(detail)
            values = self._get_detail_values(bill, detail, main, price, second)
            self.env['jc_storage.sale_out_store.detail'].create(values)
            self.env['jc_storage.sale_out_store.out_detail'].create(values)
        return bill

    def _get_bill_values(self):
        values = {
            'source_bill_id': self.id,
            'source_bill_type': 2,  # 销售订单
            'order_name': self.name,
            'customer_id': self.customer_id.id,
            'date': self.date,
            'out_store_date': self.out_store_date,
            'type_id': self.type_id.id,
            'staff_id': self.staff_id.id,
            'department_id': self.department_id.id,
            'store_id': self.store_id.id,
            'company_id': self.company_id.id,
            'remark': self.remark,
            'address': self.address,
            'total_main_number': self.total_main_number,
            'total_second_number': self.total_second_number,
            'total_money': self.total_money,
        }
        return values

    def _get_detail_values(self, bill, detail, main, price, second):
        values = {
            'sale_out_store_id': bill.id,
            'source_bill_type': 2,  # 销售订单
            'source_bill_id': self.id,
            'source_detail_id': detail.id,
            'goods_id': detail.goods_id.id,
            'second_unit_id': detail.second_unit_id.id,
            'second_unit_number': detail.second_unit_number,
            'second_unit_number_tmp': main,
            'main_unit_id': detail.main_unit_id.id,
            'main_unit_number': detail.main_unit_number,
            'main_unit_number_tmp': second,
            'price': detail.price,
            'price_tmp': price,
            'money': detail.money,
            'remark': detail.remark,
        }
        return values

    @staticmethod
    def get_str_tuple_from_number(detail):
        second = ''
        if detail.second_unit_number:
            second = str(detail.second_unit_number)
        main = ''
        if detail.main_unit_number:
            main = str(detail.main_unit_number)
        price = ''
        if detail.price:
            price = str(detail.price)
        return main, second, price

    def _delete_out_store(self):
        bills = self.env["jc_storage.sale_out_store"].search(
            [('source_bill_id', '=', self.id), ('source_bill_type', '=', 2)])
        if bills:
            for bill in bills:
                bill.unlink()

    def _check_logic(self):
        if not self.type_id:
            raise ValidationError(u'未选择{销售类型}')
        setting = self.env['setting_center.sale_type'].query_type(self.type_id.id)
        if not setting:
            raise ValidationError(u'请到【设置中心】“销售”下设置“销售流程”！')
        _type = setting[1]
        if _type == 1:
            return
        bill = self._create_out_store()
        if _type == 20:
            bill.do_check()
        return

    @api.multi
    def do_check(self):
        self._check_logic()
        super(SaleOrder, self).do_check()

    @api.multi
    def do_un_check(self):
        self._delete_out_store()
        super(SaleOrder, self).do_un_check()

    @api.multi
    def do_customer_setting(self):
        table = u'jc_sale.sale_order'
        table_show_name = u'销售订单'
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(SaleOrder, self).default_get(fields_)
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res
