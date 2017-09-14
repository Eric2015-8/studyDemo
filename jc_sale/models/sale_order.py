# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _name = 'jc_sale.sale_order'

    _inherit = ['ir.needaction_mixin']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    forecast_id = fields.Many2one('jc_sale.sale_forecast', string=u'销售预报单ID')

    customer_id = fields.Many2one('archives.customer', string=u'客户名称', required=True)
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    sale_type_id = fields.Many2one('archives.sale_type', string=u'销售类型', required=True)
    remark = fields.Char(string=u'摘要')

    sale_order_detail = fields.One2many('jc_sale.sale_order.detail', 'sale_order_id', string=u'销售订单明细', copy=True)

    company_id = fields.Many2one('archives.company', string=u'公司')
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True)
    store_id = fields.Many2one('archives.store', string=u'仓库')

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
        return super(SaleOrder, self).unlink()

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not SaleOrder._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        return super(SaleOrder, self).write(values)

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
