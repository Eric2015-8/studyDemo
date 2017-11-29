# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


# ======================== 注意 =======================================
# =====修改任何内容，需要同步修改所有同名文件里的内容。搜索下一行(第9行)即可=====
class Bill(models.Model):
    _name = 'jc_bill_base'
    _description = u'单据基类'

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    name = fields.Char(string=u'单据编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: '新建')
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    remark = fields.Char(string=u'摘要')

    @api.multi
    def unlink(self):
        if self.bill_state > 1:
            raise ValidationError('只有未审核的单据才能删除.')
        return super(Bill, self).unlink()

    @api.model
    def create(self, values):
        if values.get('name', '新建') == '新建':
            values['name'] = self.env['ir.sequence'].next_by_code('jc_sale.sale_order') or '新建'

        result = super(Bill, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not Bill._is_bill_state_change(values):
            raise ValidationError('只有未审核单据才能编辑.')
        return super(Bill, self).write(values)

    @staticmethod
    def _is_bill_state_change(values):
        if len(values) == 1 and 'bill_state' in values:
            return True
        return False

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