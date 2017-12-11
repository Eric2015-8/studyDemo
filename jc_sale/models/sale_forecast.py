# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from . import jc_base


class SaleForecast(jc_base.Bill):
    _name = 'jc_sale.sale_forecast'
    _description = u'销售：销售预报'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    customer_id = fields.Many2one('archives.customer', string=u'客户', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())

    type_id = fields.Many2one('archives.common_archive', string=u'销售类型', required=True,
                              domain=[('archive_name', '=', 1)])

    sale_forecast_detail = fields.One2many('jc_sale.sale_forecast.detail', 'sale_forecast_id', string=u'销售预报明细',
                                           copy=True)

    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True, domain="[('is_sale_man','=',True)]")
    store_id = fields.Many2one('archives.store', string=u'仓库',
                               domain=lambda self: self.env['archives.organization'].get_store_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())
    out_store_date = fields.Date(string=u'出库日期', required=True, default=fields.Date.today)

    @api.model
    def get_code(self):
        return self._name

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

    def _create_order(self):
        values = {
            'source_bill_id': self.id,
            'source_bill_type': 1,  # 销售预报
            'customer_id': self.customer_id.id,
            'date': self.date,
            'out_store_date': self.out_store_date,
            'type_id': self.type_id.id,
            'staff_id': self.staff_id.id,
            'department_id': self.department_id.id,
            'store_id': self.store_id.id,
            'company_id': self.company_id.id,
            'remark': self.remark,
        }
        order = self.env['jc_sale.sale_order'].create(values)
        for detail in self.sale_forecast_detail:
            values = {
                'sale_order_id': order.id,
                'source_bill_type': 1,  # 销售预报
                'source_bill_id': self.id,
                'source_detail_id': detail.id,
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
        return order

    def _delete_order(self):
        orders = self.env["jc_sale.sale_order"].search([('source_bill_id', '=', self.id), ('source_bill_type', '=', 1)])
        if orders:
            for bill in orders:
                bill.unlink()

    def _check_logic(self):
        if not self.type_id:
            raise ValidationError(u'未选择{销售类型}')
        setting = self.env['setting_center.sale_type'].query_type(self.type_id.id)
        if not setting:
            raise ValidationError(u'请到【设置中心】“销售”下设置“销售流程”！')
        _type = setting[0]
        if _type == 1:
            return
        order = self._create_order()
        if _type == 20:
            order.do_check()
        return

    @api.multi
    def do_check(self):
        self._check_logic()
        super(SaleForecast, self).do_check()

    @api.multi
    def do_un_check(self):
        self._delete_order()
        super(SaleForecast, self).do_un_check()

    def do_customer_setting(self):
        table = u'jc_sale.sale_forecast'
        table_show_name = u'销售预报'
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)

    @api.model
    def default_get(self, fields):
        res = super(SaleForecast, self).default_get(fields)
        need_set_fields = ['customer_id', 'type_id', 'company_id', 'staff_id', 'store_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields, need_set_fields)
        return res


class SaleForecastDetail(models.Model):
    _name = 'jc_sale.sale_forecast.detail'
    _description = u'销售：销售预报明细'

    _inherit = ['goods.detail']

    sale_forecast_id = fields.Many2one('jc_sale.sale_forecast', string='销售预报引用', required=True,
                                       ondelete='cascade', index=True, copy=False)

    remark = fields.Char(string=u'备注')
