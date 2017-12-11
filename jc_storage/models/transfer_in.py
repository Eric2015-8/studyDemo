# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import bill_define
from . import jc_base


class TransferIn(jc_base.Bill):
    _name = 'jc_storage.transfer_in'
    _description = u'仓储：调拨入库'
    _order = 'id desc'

    _inherit = ['ir.needaction_mixin']

    source_bill_type = fields.Selection(bill_define.BILL_TYPE, string=u'来源单据类型', readonly=True, copy=False)
    source_bill_id = fields.Integer(string="来源单据号", readonly=True, copy=False, default=0)

    out_store_id = fields.Many2one('archives.store', string=u'调出仓库', required=True,
                                   domain=lambda self: self.env['archives.organization'].get_store_organization())
    in_store_id = fields.Many2one('archives.store', string=u'调入仓库', required=True,
                                  domain=lambda self: self.env['archives.organization'].get_store_organization())
    transfer_out_type_id = fields.Many2one('archives.common_archive', string=u'调出类型', required=True,
                                           domain="[('archive_name','=',20)]")
    transfer_in_type_id = fields.Many2one('archives.common_archive', string=u'调入类型', required=True,
                                          domain="[('archive_name','=',21)]")

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

    @api.model
    def get_code(self):
        return self._name

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

    def do_customer_setting(self):
        table_show_name = u'调拨入库'
        return self.env['jc_storage.set_transfer_customer_setting'].send_and_open(self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(TransferIn, self).default_get(fields_)
        self.env['jc_storage.set_transfer_customer_setting'].set_default(res, self._name, fields_)
        return res
