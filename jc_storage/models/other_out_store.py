# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import jc_base


class OtherOutStore(jc_base.Bill):
    _name = 'jc_storage.other_out_store'
    _description = u'仓储：其他出库'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    store_id = fields.Many2one('archives.store', string=u'仓库', required=True,
                               domain=lambda self: self.env['archives.organization'].get_store_organization())
    in_store_type_id = fields.Many2one('archives.common_archive', string=u'入库类型', required=True,
                                       domain="[('archive_name','=',18)]")

    customer_id = fields.Many2one('archives.customer', string=u'往来单位',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    staff_id = fields.Many2one('archives.staff', string=u'员工', domain=[('is_sale_man', '=', True)])
    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    total_second_number = fields.Float(string='辅数量', store=True, readonly=True, compute='_amount_all',
                                       track_visibility='always')
    total_main_number = fields.Float(string='主数量', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    total_money = fields.Float(string='金额', store=True, readonly=True, compute='_amount_all', track_visibility='always')

    other_out_store_detail = fields.One2many('jc_storage.other_out_store.detail', 'other_out_store_id',
                                             string=u'其他入库明细', copy=True)

    @api.model
    def get_code(self):
        return self._name

    @api.depends('other_out_store_detail.second_unit_number', 'other_out_store_detail.main_unit_number',
                 'other_out_store_detail.money')
    def _amount_all(self):
        """
        Compute the total amounts of the OtherOutStore.
        """
        for bill in self:
            total_second = 0.0
            total_main = 0.0
            total_money = 0.0
            for line in bill.other_out_store_detail:
                total_second += line.second_unit_number
                total_main += line.main_unit_number
                total_money += line.money
            bill.update({
                'total_second_number': total_second,
                'total_main_number': total_main,
                'total_money': total_money,
            })

    @api.model
    def _needaction_domain_get(self):
        return [('bill_state', '=', 1)]

    @api.multi
    def add_goods_page(self):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('archives.archives_common_goods_number_action_window')
        list_view_id = imd.xmlid_to_res_id('archives.archives_common_goods_number_list')

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
                # 'customer_id': self.customer_id.id,
                'detail': 'jc_storage.other_out_store.detail',
            },
            'res_model': action.res_model,
        }
        return result

    @api.multi
    def do_customer_setting(self):
        table = u'jc_storage.other_out_store'
        table_show_name = u'其他出库'
        need_set_fields = ['store_id', 'in_store_type_id', 'staff_id', 'customer_id', 'company_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(OtherOutStore, self).default_get(fields_)
        need_set_fields = ['store_id', 'in_store_type_id', 'staff_id', 'customer_id', 'company_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res
