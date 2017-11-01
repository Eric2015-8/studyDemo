# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOutStore(models.Model):
    _name = 'jc_storage.sale_out_store'
    _description = u'仓储：销售出库单'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    name = fields.Char(string=u'订单编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('新建'))

    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    sale_type_id = fields.Many2one('archives.common_archive', string=u'销售类型', required=True)
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

    sale_out_store_detail = fields.One2many('jc_storage.sale_out_store.detail', 'sale_out_store_id', string=u'销售出库单明细',
                                            copy=True)

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

    @staticmethod
    def _is_bill_state_change(values):
        if len(values) == 1 and 'bill_state' in values:
            return True
        return False

    @api.multi
    def unlink(self):
        if self.bill_state > 1:
            raise ValidationError(_('只有未审核的单据才能删除.'))
        return super(SaleOutStore, self).unlink()

    @api.model
    def create(self, values):
        if values.get('name', '新建') == '新建':
            values['name'] = self.env['ir.sequence'].next_by_code('jc_storage.sale_out_store') or '新建'

        result = super(SaleOutStore, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not SaleOutStore._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        return super(SaleOutStore, self).write(values)

    @api.multi
    def do_check(self):
        self.bill_state = 10

    @api.multi
    def do_finish(self):
        self.bill_state = 20

    @api.multi
    def do_un_finish(self):
        self.bill_state = 10

    @api.multi
    def do_un_check(self):
        self.bill_state = 1

    @api.multi
    def do_customer_setting(self):
        table = u'jc_storage.sale_out_store'
        table_show_name = u'销售出库单'
        need_set_fields = ['customer_id', 'sale_type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(SaleOutStore, self).default_get(fields_)
        need_set_fields = ['customer_id', 'sale_type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res