# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import jc_base


class TransferOut(jc_base.Bill):
    _name = 'jc_storage.transfer_out'
    _description = u'仓储：调拨出库'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    out_store_id = fields.Many2one('archives.store', string=u'调出仓库', required=True,
                                   domain=lambda self: self.env['archives.organization'].get_store_organization())
    in_store_id = fields.Many2one('archives.store', string=u'调入仓库', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_store_organization())
    transfer_out_type_id = fields.Many2one('archives.common_archive', string=u'调出类型', required=True,
                                           domain="[('archive_name','=',20)]")
    transfer_in_type_id = fields.Many2one('archives.common_archive', string=u'调入类型', domain="[('archive_name','=',21)]")

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

    transfer_out_detail = fields.One2many('jc_storage.transfer_out.detail', 'transfer_out_id',
                                          string=u'调拨出库明细', copy=True)

    @api.model
    def get_code(self):
        return self._name

    @api.depends('transfer_out_detail.second_unit_number', 'transfer_out_detail.main_unit_number',
                 'transfer_out_detail.money')
    def _amount_all(self):
        """
        Compute the total amounts of the TransferOut.
        """
        for bill in self:
            total_second = 0.0
            total_main = 0.0
            total_money = 0.0
            for line in bill.transfer_out_detail:
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

    def _create_transfer_in(self):
        values = {
            'source_bill_id': self.id,
            'source_bill_type': 26,  # 调拨出库
            'out_store_id': self.out_store_id.id,
            'in_store_id': self.in_store_id.id,
            'transfer_out_type_id': self.transfer_out_type_id.id,
            'transfer_in_type_id': self.transfer_in_type_id.id,
            'date': self.date,
            'out_unit_id': self.out_unit_id.id,
            'in_unit_id': self.in_unit_id.id,
            'out_staff_id': self.out_staff_id.id,
            'int_staff_id': self.int_staff_id.id,
            'company_id': self.company_id.id,
            'department_id': self.department_id.id,
            'remark': self.remark,
            'total_main_number': self.total_main_number,
            'total_second_number': self.total_second_number,
            'total_money': self.total_money,
        }
        bill = self.env['jc_storage.transfer_in'].create(values)
        for detail in self.transfer_out_detail:
            values = {
                'transfer_in_id': bill.id,
                'source_bill_type': 26,  # 调拨出库
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
            self.env['jc_storage.transfer_in.detail'].create(values)
        return bill

    def _delete_transfer_out(self):
        bills = self.env["jc_storage.transfer_in"].search(
            [('source_bill_id', '=', self.id), ('source_bill_type', '=', 26)])
        if bills:
            for bill in bills:
                bill.unlink()

    def _check_logic(self):
        if not self.transfer_out_type_id:
            raise ValidationError(u'未选择{调出类型}')
        setting = self.env['setting_center.transfer_out_type'].query_type(self.transfer_out_type_id.id)
        if not setting:
            raise ValidationError(u'请到【设置中心】“仓储”下设置“调拨流程”！')
        _type = setting
        if _type == 1:
            return
        bill = self._create_transfer_in()
        if _type == 20:
            bill.do_check()
        return

    @api.multi
    def do_check(self):
        self._check_logic()
        super(TransferOut, self).do_check()

    @api.multi
    def do_un_check(self):
        self._delete_transfer_out()
        super(TransferOut, self).do_check()

    def do_customer_setting(self):
        table_show_name = u'调拨出库'
        return self.env['jc_storage.set_transfer_customer_setting'].send_and_open(self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(TransferOut, self).default_get(fields_)
        self.env['jc_storage.set_transfer_customer_setting'].set_default(res, self._name, fields_)
        return res
