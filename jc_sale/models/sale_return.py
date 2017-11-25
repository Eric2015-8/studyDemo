# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleReturn(models.Model):
    _name = 'jc_sale.sale_return'
    _description = u'销售：销售退单'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin', 'jc_approve']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    name = fields.Char(string=u'单据编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('新建'))

    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    type_id = fields.Many2one('archives.common_archive', string=u'销售退货类型', required=True,
                                          domain="[('archive_name','=',22)]")
    remark = fields.Char(string=u'摘要')

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True)
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

    @staticmethod
    def _is_bill_state_change(values):
        if len(values) == 1 and 'bill_state' in values:
            return True
        return False

    @api.multi
    def unlink(self):
        if self.bill_state > 1:
            raise ValidationError(_('只有未审核的单据才能删除.'))
        return super(SaleReturn, self).unlink()

    @api.model
    def create(self, values):
        if values.get('name', '新建') == '新建':
            values['name'] = self.env['ir.sequence'].next_by_code('jc_sale.sale_return') or '新建'

        result = super(SaleReturn, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not SaleReturn._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        return super(SaleReturn, self).write(values)

    def _create_sale_account(self):
        values = {
            'source_bill_id': self.id,
            'source_bill_type': 23,  # 销售退单
            'customer_id': self.customer_id.id,
            'date': self.date,
            'out_store_date': self.date,
            # 'type_id': self.type_id.id,
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
        for detail in self.sale_return_detail:
            values = {
                'sale_account_id': bill.id,
                'source_bill_type': 23,  # 销售退单
                'source_bill_id': self.id,
                'source_detail_id': detail.id,
                'goods_id': detail.goods_id.id,
                'second_unit_id': detail.second_unit_id.id,
                'second_unit_number': detail.second_unit_number,
                'second_unit_number_tmp': detail.second_unit_number,
                'main_unit_id': detail.main_unit_id.id,
                'main_unit_number': detail.main_unit_number,
                'main_unit_number_tmp': detail.main_unit_number,
                'price': detail.price,
                'price_tmp': detail.price,
                'money': detail.money,
                'remark': detail.remark,
            }
            self.env['jc_finance.sale_account.detail'].create(values)
        return bill

    def _delete_sale_account(self):
        bills = self.env["jc_finance.sale_account"].search(
            [('source_bill_id', '=', self.id), ('source_bill_type', '=', 23)])
        if bills:
            for bill in bills:
                bill.unlink()

    def _check_logic(self):
        if not self.type_id:
            raise ValidationError(u'未选择{销售退货类型}')
        setting = self.env['setting_center.return_type'].query_type(self.type_id.id)
        if not setting:
            raise ValidationError(u'请到【设置中心】“销售”下设置“销售退货流程”！')
        _type = setting
        if _type == 1:
            return
        bill = self._create_sale_account()
        if _type == 20:
            bill.do_check()
        return

    @api.multi
    def do_check(self):
        # self._check_logic()
        self.bill_state = 10

    @api.multi
    def do_finish(self):
        self.bill_state = 20

    @api.multi
    def do_un_finish(self):
        self.bill_state = 10

    @api.multi
    def do_un_check(self):
        # self._delete_sale_account()
        self.bill_state = 1

    @api.multi
    def do_customer_setting(self):
        table = u'jc_sale.sale_return'
        table_show_name = u'销售退单'
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(SaleReturn, self).default_get(fields_)
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res
