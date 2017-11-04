# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockCheck(models.Model):
    _name = 'jc_storage.stock_check'
    _description = u'仓储：库存盘点'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    name = fields.Char(string=u'单据编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('新建'))

    store_id = fields.Many2one('archives.store', string=u'仓库',
                               domain=lambda self: self.env['archives.organization'].get_store_organization())
    stock_date = fields.Date(string=u'库存日期', required=True, default=fields.Date.today)
    staff_id = fields.Many2one('archives.staff', string=u'经办人', required=True)
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)

    remark = fields.Char(string=u'摘要')

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())

    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    stock_check_detail = fields.One2many('jc_storage.stock_check.detail', 'stock_check_id', string=u'库存盘点明细',
                                         copy=True)

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
        return super(StockCheck, self).unlink()

    @api.model
    def create(self, values):
        if values.get('name', '新建') == '新建':
            values['name'] = self.env['ir.sequence'].next_by_code('jc_storage.stock_check') or '新建'

        result = super(StockCheck, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not StockCheck._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        return super(StockCheck, self).write(values)

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
        table_show_name = u'库存盘点'
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(StockCheck, self).default_get(fields_)
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res


need_set_fields = ['store_id', 'company_id', 'department_id', 'staff_id']
