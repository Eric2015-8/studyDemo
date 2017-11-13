# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransferOut(models.Model):
    _name = 'jc_storage.transfer_out'
    _description = u'仓储：调拨出库'
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
    transfer_in_type_id = fields.Many2one('archives.common_archive', string=u'调入类型', domain="[('archive_name','=',21)]")

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

    transfer_out_detail = fields.One2many('jc_storage.transfer_out.detail', 'transfer_out_id',
                                          string=u'调拨出库明细', copy=True)

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

    @staticmethod
    def _is_bill_state_change(values):
        if len(values) == 1 and 'bill_state' in values:
            return True
        return False

    @api.model
    def create(self, values):
        if values.get('name', '新建') == '新建':
            values['name'] = self.env['ir.sequence'].next_by_code('jc_storage.transfer_out') or '新建'
        result = super(TransferOut, self).create(values)
        # self._check_goods_position()
        return result

    @api.multi
    def unlink(self):
        if self.bill_state > 1:
            raise ValidationError(_('只有未审核的单据才能删除.'))
        return super(TransferOut, self).unlink()

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not TransferOut._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        result = super(TransferOut, self).write(values)
        # self._check_goods_position()
        return result

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
        self.bill_state = 10

    @api.multi
    def do_finish(self):
        self.bill_state = 20

    @api.multi
    def do_un_finish(self):
        self.bill_state = 10

    @api.multi
    def do_un_check(self):
        self._delete_transfer_out()
        self.bill_state = 1

    @api.multi
    def do_customer_setting(self):
        table_show_name = u'调拨出库'
        return self.env['jc_storage.set_transfer_customer_setting'].send_and_open(self._name, table_show_name)

    @api.model
    def default_get(self, fields_):
        res = super(TransferOut, self).default_get(fields_)
        self.env['jc_storage.set_transfer_customer_setting'].set_default(res, self._name, fields_)
        return res
