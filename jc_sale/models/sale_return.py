# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import jc_base


class SaleReturn(jc_base.Bill):
    _name = 'jc_sale.sale_return'
    _description = u'销售：销售退单'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin', 'jc_approve']

    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    type_id = fields.Many2one('archives.common_archive', string=u'销售退货类型', required=True,
                              domain="[('archive_name','=',22)]")

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True, domain=[('is_sale_man', '=', True)])
    store_id = fields.Many2one('archives.store', string=u'仓库',
                               domain=lambda self: self.env['archives.organization'].get_store_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    total_second_number = fields.Float(string='辅数量', store=True, readonly=True, compute='_amount_all',
                                       track_visibility='always')
    total_main_number = fields.Float(string='主数量', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    total_money = fields.Float(string='金额', store=True, readonly=True, compute='_amount_all', track_visibility='always')

    sale_return_detail = fields.One2many('jc_sale.sale_return.detail', 'sale_return_id', string=u'销售退单明细', copy=True)

    @api.model
    def get_code(self):
        return self._name

    @api.depends('sale_return_detail.second_unit_number', 'sale_return_detail.main_unit_number',
                 'sale_return_detail.money')
    def _amount_all(self):
        for bill in self:
            total_second = 0.0
            total_main = 0.0
            total_money = 0.0
            for line in bill.sale_return_detail:
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

    def _create_sale_return_store(self):
        values = {
            'source_bill_id': self.id,
            'source_bill_type': 3,  # 销售退单
            'order_name': self.name,
            'customer_id': self.customer_id.id,
            'date': self.date,
            'sale_return_type_id': self.type_id.id,
            'staff_id': self.staff_id.id,
            'department_id': self.department_id.id,
            'store_id': self.store_id.id,
            'company_id': self.company_id.id,
            'remark': self.remark,
            'total_main_number': self.total_main_number,
            'total_second_number': self.total_second_number,
            'total_money': self.total_money,
        }
        bill = self.env['jc_storage.sale_return_store'].create(values)
        for detail in self.sale_return_detail:
            values = self._get_detail_values(bill, detail)
            self.env['jc_storage.sale_return_store.detail'].create(values)
            self.env['jc_storage.sale_return_store.return_detail'].create(values)
        return bill

    def _get_detail_values(self, bill, detail):
        values = {
            'sale_return_store_id': bill.id,
            'source_bill_type': 3,  # 销售退单
            'source_bill_id': self.id,
            'source_detail_id': detail.id,
            'goods_id': detail.goods_id.id,
            'second_unit_id': detail.second_unit_id.id,
            'second_unit_number': detail.second_unit_number,
            # 'second_unit_number_tmp': detail.second_unit_number,
            'main_unit_id': detail.main_unit_id.id,
            'main_unit_number': detail.main_unit_number,
            # 'main_unit_number_tmp': detail.main_unit_number,
            'price': detail.price,
            # 'price_tmp': detail.price,
            'money': detail.money,
            'remark': detail.remark,
        }
        return values

    def _delete_sale_return_store(self):
        bills = self.env["jc_storage.sale_return_store"].search(
            [('source_bill_id', '=', self.id), ('source_bill_type', '=', 3)])
        if bills:
            for bill in bills:
                bill.unlink()

    def _check_logic(self):
        if not self.type_id:
            raise ValidationError(u'未选择{销售退货类型}')
        setting = self.env['setting_center.return_type'].query_type(self.type_id.id)
        if not setting:
            raise ValidationError(u'请到【设置中心】“销售”下设置“销售退货流程”！')
        _type = setting[0]
        if _type == 1:
            return
        bill = self._create_sale_return_store()
        if _type == 20:
            bill.do_check()
        return

    @api.multi
    def do_check(self):
        self._check_logic()
        super(SaleReturn, self).do_check()

    @api.multi
    def do_un_check(self):
        self._delete_sale_return_store()
        super(SaleReturn, self).do_un_check()

    @api.multi
    def do_customer_setting(self):
        table = u'jc_sale.sale_return'
        table_show_name = u'销售退单'
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        type_id_field = 'sale_return_type_id'
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name,
                                                                       type_id_field)

    @api.model
    def default_get(self, fields_):
        res = super(SaleReturn, self).default_get(fields_)
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        type_id_field = 'sale_return_type_id'
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields, type_id_field)
        return res
