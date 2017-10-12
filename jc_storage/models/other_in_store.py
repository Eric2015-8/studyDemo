# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OtherInStore(models.Model):
    _name = 'jc_storage.other_in_store'
    _description = u'仓储：其它入库'

    _inherit = ['ir.needaction_mixin']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    store_id = fields.Many2one('archives.store', string=u'仓库', required=True,
                               domain=lambda self: self.env['archives.organization'].get_store_organization(),
                               default=lambda self: self.env['archives.set_customer_setting'].query_default(self._name,
                                                                                                            'store_id'))
    in_store_type_id = fields.Many2one('archives.common_archive', string=u'入库类型', required=True,
                                       domain="[('archive_name','=',18)]")
    staff_id = fields.Many2one('archives.staff', string=u'经办人',
                               default=lambda self: self.env['archives.set_customer_setting'].query_default(self._name,
                                                                                                            'staff_id'))
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    remark = fields.Char(string=u'摘要')

    other_in_store_detail = fields.One2many('jc_storage.other_in_store.detail', 'other_in_store_id',
                                            string=u'其它入库明细', copy=True)

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
                'detail': 'jc_storage.other_in_store.detail',
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
        result = super(OtherInStore, self).create(values)
        return result

    @api.multi
    def unlink(self):
        if self.bill_state > 1:
            raise ValidationError(_('只有未审核的单据才能删除.'))
        return super(OtherInStore, self).unlink()

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not OtherInStore._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        return super(OtherInStore, self).write(values)

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
        table = u'jc_storage.other_in_store'
        table_show_name = u'其它入库'
        need_set_fields = ['store_id', 'in_store_type_id', 'staff_id']
        return self.env['archives.set_customer_setting'].send_and_open(need_set_fields, table, table_show_name)
