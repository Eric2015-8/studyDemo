# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OtherOutStore(models.Model):
    _name = 'jc_storage.other_out_store'
    _description = u'仓储：其它出库'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    name = fields.Char(string=u'单据编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('新建'))

    store_id = fields.Many2one('archives.store', string=u'仓库', required=True,
                               domain=lambda self: self.env['archives.organization'].get_store_organization())
    in_store_type_id = fields.Many2one('archives.common_archive', string=u'入库类型', required=True,
                                       domain="[('archive_name','=',18)]")
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    remark = fields.Char(string=u'摘要')

    customer_id = fields.Many2one('archives.customer', string=u'往来单位',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    staff_id = fields.Many2one('archives.staff', string=u'员工')
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
                                             string=u'其它入库明细', copy=True)

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

    @staticmethod
    def _is_bill_state_change(values):
        if len(values) == 1 and 'bill_state' in values:
            return True
        return False

    @api.model
    def create(self, values):
        if values.get('name', '新建') == '新建':
            values['name'] = self.env['ir.sequence'].next_by_code('jc_storage.other_out_store') or '新建'
        result = super(OtherOutStore, self).create(values)
        return result

    @api.multi
    def unlink(self):
        if self.bill_state > 1:
            raise ValidationError(_('只有未审核的单据才能删除.'))
        return super(OtherOutStore, self).unlink()

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not OtherOutStore._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        return super(OtherOutStore, self).write(values)

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
        table = u'jc_storage.other_out_store'
        table_show_name = u'其它出库'
        need_set_fields = ['store_id', 'in_store_type_id', 'staff_id', 'customer_id', 'company_id', 'department_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(OtherOutStore, self).default_get(fields_)
        need_set_fields = ['store_id', 'in_store_type_id', 'staff_id', 'customer_id', 'company_id', 'department_id']
        self.env['archives.set_customer_setting'].set_default(res, self._name, fields_, need_set_fields)
        return res
