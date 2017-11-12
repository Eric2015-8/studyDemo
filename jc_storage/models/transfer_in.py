# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransferIn(models.Model):
    _name = 'jc_storage.transfer_in'
    _description = u'仓储：调拨入库'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    name = fields.Char(string=u'单据编号', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('新建'))

    out_store_id = fields.Many2one('archives.store', string=u'调出仓库', required=True,
                                   domain=lambda self: self.env['archives.organization'].get_store_organization())
    in_store_id = fields.Many2one('archives.store', string=u'调入仓库', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_store_organization())
    transfer_out_type_id = fields.Many2one('archives.common_archive', string=u'调出类型', required=True,
                                           domain="[('archive_name','=',20)]")
    transfer_in_type_id = fields.Many2one('archives.common_archive', string=u'调入类型', required=True,
                                          domain="[('archive_name','=',21)]")

    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    remark = fields.Char(string=u'摘要')

    out_unit_id = fields.Many2one('archives.customer', string=u'调出单位',
                                  domain=lambda self: self.env['archives.organization'].get_customer_organization())
    in_unit_id = fields.Many2one('archives.customer', string=u'调入单位',
                                 domain=lambda self: self.env['archives.organization'].get_customer_organization())

    out_staff_id = fields.Many2one('archives.staff', string=u'调出员工')
    int_staff_id = fields.Many2one('archives.staff', string=u'调入员工')
    company_id = fields.Many2one('res.company', string=u'公司', required=True,
                                 domain=lambda self: self.env['archives.organization'].get_company_organization())
    department_id = fields.Many2one('archives.department', string=u'部门', required=True,
                                    domain=lambda self: self.env['archives.organization'].get_department_organization())

    total_second_number = fields.Float(string='辅数量', store=True, readonly=True, compute='_amount_all',
                                       track_visibility='always')
    total_main_number = fields.Float(string='主数量', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    total_money = fields.Float(string='金额', store=True, readonly=True, compute='_amount_all', track_visibility='always')

    transfer_in_detail = fields.One2many('jc_storage.transfer_in.detail', 'transfer_in_id',
                                         string=u'调拨入库明细', copy=True)

    @api.depends('transfer_in_detail.second_unit_number', 'transfer_in_detail.main_unit_number',
                 'transfer_in_detail.money')
    def _amount_all(self):
        """
        Compute the total amounts of the TransferIn.
        """
        for bill in self:
            total_second = 0.0
            total_main = 0.0
            total_money = 0.0
            for line in bill.transfer_in_detail:
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

    @staticmethod
    def _is_bill_state_change(values):
        if len(values) == 1 and 'bill_state' in values:
            return True
        return False

    @api.model
    def create(self, values):
        if values.get('name', '新建') == '新建':
            values['name'] = self.env['ir.sequence'].next_by_code('jc_storage.transfer_in') or '新建'
        result = super(TransferIn, self).create(values)
        # self._check_goods_position()
        return result

    @api.multi
    def unlink(self):
        if self.bill_state > 1:
            raise ValidationError(_('只有未审核的单据才能删除.'))
        return super(TransferIn, self).unlink()

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not TransferIn._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        result = super(TransferIn, self).write(values)
        # self._check_goods_position()
        return result

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
        table_show_name = u'调拨入库'
        return self.env['jc_storage.set_transfer_customer_setting'].send_and_open(self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(TransferIn, self).default_get(fields_)
        self.env['jc_storage.set_transfer_customer_setting'].set_default(res, self._name, fields_)
        return res
