# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import jc_base


class StockCheck(jc_base.Bill):
    _name = 'jc_storage.stock_check'
    _description = u'仓储：库存盘点'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    store_id = fields.Many2one('archives.store', string=u'仓库',
                               domain=lambda self: self.env['archives.organization'].get_store_organization())
    stock_date = fields.Date(string=u'库存日期', required=True, default=fields.Date.today)
    staff_id = fields.Many2one('archives.staff', string=u'经办人', required=True)

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())

    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    stock_check_detail = fields.One2many('jc_storage.stock_check.detail', 'stock_check_id', string=u'库存盘点明细',
                                         copy=True)

    @api.model
    def _needaction_domain_get(self):
        return [('bill_state', '=', 1)]

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
