# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleForecast(models.Model):
    _name = 'jc_sale.sale_forecast'
    _description = u'销售：销售预报'

    _inherit = ['ir.needaction_mixin']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    name = fields.Char(string=u'预报编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('新建'))
    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization(),
                                  default=lambda self: self.env['archives.set_customer_setting'].query_default(
                                      self._name, 'customer_id'))
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    sale_type_id = fields.Many2one('archives.common_archive', string=u'销售类型', required=True,
                                   domain=[('archive_name', '=', 1)],
                                   default=lambda self: self.env['archives.set_customer_setting'].query_default(
                                       self._name, 'sale_type_id'))
    remark = fields.Char(string=u'摘要')

    sale_forecast_detail = fields.One2many('jc_sale.sale_forecast.detail', 'sale_forecast_id', string=u'销售预报明细',
                                           copy=True)

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 default=lambda self: self._set_company())
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True,
                               default=lambda self: self.env['archives.set_customer_setting'].query_default(self._name,
                                                                                                            'staff_id'))
    store_id = fields.Many2one('archives.store', string=u'仓库',
                               default=lambda self: self.env['archives.set_customer_setting'].query_default(self._name,
                                                                                                            'store_id'))
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    default=lambda self: self.env['archives.set_customer_setting'].query_default(
                                        self._name, 'department_id'))

    def _set_company(self):
        id = self.env['archives.set_customer_setting'].query_default(self._name, 'company_id')
        if id:
            return id
        return self.env['res.company']._company_default_get()

    @api.onchange('customer_id')
    def _onchange_for_staff(self):
        self.staff_id = self.customer_id.staff_id

    @api.multi
    def add_goods_page(self):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('archives.archives_common_goods_number_action_window')
        list_view_id = imd.xmlid_to_res_id('archives.archives_common_goods_number_list')
        # form_view_id = imd.xmlid_to_res_id('archives.archives_common_goods_edit')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            # 'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'views': [[list_view_id, 'tree']],
            'target': action.target,
            # 'context': action.context,
            'context': {
                'id': self.id,
                'customer_id': self.customer_id.id,
                'detail': 'jc_sale.sale_forecast.detail',
            },
            'res_model': action.res_model,
        }
        # if len(invoice_ids) > 1:
        #     result['domain'] = "[('id','in',%s)]" % invoice_ids.ids
        # elif len(invoice_ids) == 1:
        #     result['views'] = [(form_view_id, 'form')]
        #     result['res_id'] = invoice_ids.ids[0]
        # else:
        #     result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.model
    def _needaction_domain_get(self):
        return [('bill_state', '=', 1)]

    @staticmethod
    def _is_bill_state_change(values):
        if len(values) == 1 and 'bill_state' in values:
            return True
        return False

    def _create_order(self):
        values = {
            'forecast_id': self.id,
            'customer_id': self.customer_id.id,
            'date': self.date,
            'sale_type_id': self.sale_type_id.id,
            'staff_id': self.staff_id.id,
            'department_id': self.department_id,
            'remark': self.remark,
        }
        order = self.env['jc_sale.sale_order'].create(values)
        for detail in self.sale_forecast_detail:
            values = {
                'sale_order_id': order.id,
                'forecast_id': self.id,
                'forecast_detail_id': detail.id,
                'goods_id': detail.goods_id.id,
                'second_unit_id': detail.second_unit_id.id,
                'second_unit_number': detail.second_unit_number,
                'main_unit_id': detail.main_unit_id.id,
                'main_unit_number': detail.main_unit_number,
                'price': detail.price,
                'money': detail.money,
                'remark': detail.remark,
            }
            self.env['jc_sale.sale_order.detail'].create(values)

    def _delete_order(self):
        orders = self.env["jc_sale.sale_order"].search([('forecast_id', '=', self.id)])
        if orders:
            for bill in orders:
                bill.unlink()

    @api.model
    def create(self, values):
        if values.get('name', '新建') == '新建':
            values['name'] = self.env['ir.sequence'].next_by_code('jc_sale.sale_forecast') or '新建'

        result = super(SaleForecast, self).create(values)
        return result

    @api.multi
    def unlink(self):
        if self.bill_state > 1:
            raise ValidationError(_('只有未审核的单据才能删除.'))
        return super(SaleForecast, self).unlink()

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not SaleForecast._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        return super(SaleForecast, self).write(values)

    @api.multi
    def do_check(self):
        self._create_order()
        self.bill_state = 10

    @api.multi
    def do_finish(self):
        self.bill_state = 20

    @api.multi
    def do_un_finish(self):
        self.bill_state = 10

    @api.multi
    def do_un_check(self):
        self._delete_order()
        self.bill_state = 1

    @api.multi
    def do_customer_setting(self):
        table = u'jc_sale.sale_forecast'
        table_show_name = u'销售预报'
        need_set_fields = ['customer_id', 'sale_type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)


class SaleForecastDetail(models.Model):
    _name = 'jc_sale.sale_forecast.detail'
    _description = u'销售：销售预报明细'

    sale_forecast_id = fields.Many2one('jc_sale.sale_forecast', string='销售预报引用', required=True,
                                       ondelete='cascade', index=True, copy=False)

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True,
                               domain=lambda self: self.env['archives.organization'].get_goods_organization())
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位', compute='_set_second')
    second_unit_number = fields.Float(digits=(6, 2), string=u'辅数量')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main')
    main_unit_number = fields.Float(digits=(6, 2), string=u'主数量')

    price = fields.Float(digits=(6, 2), help="单价", string=u'单价')
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额')

    remark = fields.Char(string=u'备注')

    @api.depends('goods_id')
    def _set_main(self):
        for record in self:
            record.main_unit_id = record.goods_id.main_unit_id

    @api.depends('goods_id')
    def _set_second(self):
        for record in self:
            record.second_unit_id = record.goods_id.second_unit_id

    @api.onchange('price', 'main_unit_number')
    def _onchange_for_money(self):
        self.money = self.price * self.main_unit_number

    @api.onchange('second_unit_number')
    def _onchange_second(self):
        if not self.goods_id.need_second_change:
            return
        if self.goods_id.second_rate != 0:
            self.main_unit_number = self.goods_id.second_rate * self.second_unit_number

    @api.onchange('main_unit_number')
    def _onchange_main(self):
        if not self.goods_id.need_second_change:
            return
        if self.goods_id.second_rate != 0:
            self.second_unit_number = self.main_unit_number / self.goods_id.second_rate

    @api.onchange('goods_id')
    def _onchange_goods(self):
        # self.second_unit_id = self.env['archives.goods'].second_unit_id
        # self.main_unit_id = self.env['archives.goods'].main_unit_id
        self.second_unit_id = self.goods_id.second_unit_id
        self.main_unit_id = self.goods_id.main_unit_id
