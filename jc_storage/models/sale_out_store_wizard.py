# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
import datetime


class CreateSaleOutStoreWizard1(models.TransientModel):
    """手机创建销售出库单 向导 """
    _name = "jc_storage.create.sale.out.store.wizard1"
    _description = u'手机创建销售出库单的向导'

    state = fields.Selection(
        [('step1', 'step1'), ('step2', 'step2')]
    )

    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    type_id = fields.Many2one('archives.common_archive', string=u'销售类型', required=True,
                                   domain=[('archive_name', '=', 1)])

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True)
    store_id = fields.Many2one('archives.store', string=u'仓库',
                               domain=lambda self: self.env['archives.organization'].get_store_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())
    remark = fields.Char(string=u'摘要')

    goods_id = fields.Many2one('archives.goods', string=u'产品')
    number = fields.Char(string=u'数量')
    price = fields.Char(string=u'单价')
    wizard_detail = fields.One2many('jc_storage.create.sale.out.store.wizard2', 'detail_id', string=u'明细', copy=True)

    @api.multi
    def action_add(self):
        self._check_values()
        self._add_detail()
        self._set_empty()
        return self._open_wizard()

    def _add_detail(self):
        number = float(self.number)
        price = float(self.price)

        values = {
            'detail_id': self.id,
            'goods_id': self.goods_id.id,
            'main_unit_number': number,
            'price': price,
        }
        self.env['jc_storage.create.sale.out.store.wizard2'].create(values)

        return

    @staticmethod
    def is_number(n):  # 是否为数字，包括整数和小数
        a = n
        if isinstance(n, unicode):
            a = n.encode('utf-8')
        if a.isdigit():
            return True
        return CreateSaleOutStoreWizard1._is_float(a)

    @staticmethod
    def _is_float(n):
        value = re.compile(r'^[-+]?[0-9]+\.[0-9]+$')
        return value.match(n)

    def _open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'jc_storage.create.sale.out.store.wizard1',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    @staticmethod
    def _open_bill(bill_id):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'jc_storage.sale_out_store',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': bill_id,
            'views': [(False, 'form')],
        }

    def _check_values(self):
        if not self.goods_id:
            raise ValidationError('请选择产品')
        if self.number and not CreateSaleOutStoreWizard1.is_number(self.number):
            raise ValidationError('{数量}并不是数字')
        if self.price and not CreateSaleOutStoreWizard1.is_number(self.price):
            raise ValidationError('{单价}并不是数字')

    def _set_empty(self):
        self.goods_id = None
        self.number = None
        self.price = None

    @api.multi
    def action_next(self):
        self.write({'state': 'step2', })
        return self._open_wizard()

    @api.multi
    def action_previous(self):
        self.write({'state': 'step1', })
        return self._open_wizard()

    @api.multi
    def create_bill(self):
        values = {
            'customer_id': self.customer_id.id,
            'date': datetime.datetime.today(),
            'type_id': self.type_id.id,
            'staff_id': self.staff_id.id,
            'department_id': self.department_id.id,
            'store_id': self.store_id.id,
            'company_id': self.company_id.id,
            'remark': self.remark,
        }
        table = u'jc_storage.sale_out_store'  # 使用销售销售出库单的个性设置
        need_set_fields = ['type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        # need_set_fields中的值，从个性设置中取值
        self.env['archives.set_customer_setting'].set_default_if_empty(values, table, need_set_fields)
        order = self.env['jc_storage.sale_out_store'].create(values)
        for detail in self.wizard_detail:
            second_unit_number = None
            if detail.goods_id.need_change() and detail.goods_id.second_rate != 0:
                second_unit_number = detail.main_unit_number / detail.goods_id.second_rate
            values = {
                'sale_out_store_id': order.id,
                'goods_id': detail.goods_id.id,
                'main_unit_number': detail.main_unit_number,
                'price': detail.price,
                'money': detail.main_unit_number * detail.price,
            }
            if second_unit_number:
                values['second_unit_number'] = second_unit_number
            self.env['jc_storage.sale_out_store.detail'].create(values)
        return CreateSaleOutStoreWizard1._open_bill(order.id)

    @api.model
    def default_get(self, fields_):
        res = super(CreateSaleOutStoreWizard1, self).default_get(fields_)
        table = u'jc_storage.sale_out_store'  # 使用销售出库单的个性设置
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, table, fields_, need_set_fields)
        return res


class CreateSaleOutStoreWizard2(models.TransientModel):
    """手机生成销售出库单 向导-明细 """
    _name = "jc_storage.create.sale.out.store.wizard2"
    _description = u'手机创建销售出库单的向导-明细'

    detail_id = fields.Many2one('jc_storage.create.sale.out.store.wizard1', string='引用', required=True,
                                ondelete='cascade', index=True, copy=False)
    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True)
    main_unit_number = fields.Float(digits=(6, 2), string=u'主数量')
    price = fields.Float(digits=(6, 2), help="单价", string=u'单价')
