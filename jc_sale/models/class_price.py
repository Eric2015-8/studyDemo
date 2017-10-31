# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ClassPrice(models.Model):
    _name = 'jc_sale.class_price'
    _description = u'销售：分类价'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    name = fields.Char(string=u'名称', required=True, copy=False, default=lambda self: _('新建'))

    price_type_id = fields.Many2one('archives.common_archive', string=u'价格分类', domain="[('archive_name','=',19)]")

    date = fields.Date(string=u'执行日期', required=True, default=fields.Date.today)
    remark = fields.Char(string=u'摘要')

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    class_price_detail = fields.One2many('jc_sale.class_price.detail', 'class_price_id', string=u'分类价明细', copy=True)

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
        return super(ClassPrice, self).unlink()

    @api.model
    def create(self, values):
        if values.get('name', '新建') == '新建':
            values['name'] = self.env['ir.sequence'].next_by_code('jc_sale.class_price') or '新建'

        result = super(ClassPrice, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not ClassPrice._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        return super(ClassPrice, self).write(values)

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
        table = u'jc_sale.class_price'
        table_show_name = u'分类价'
        need_set_fields = ['company_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(ClassPrice, self).default_get(fields_)
        need_set_fields = ['company_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields, need_set_fields)
        return res
