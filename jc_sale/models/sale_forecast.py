# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleForecast(models.Model):
    _name = 'jc_sale.sale_forecast'

    _inherit = ['ir.needaction_mixin']

    bill_state = fields.Selection(
        [(1, '未审核'), (10, '已审核'), (20, '已完毕')],
        string=u'单据状态', require=True, default=1, readonly=True
    )

    # name = fields.Char(string=u'销售预报', required=True, help=u'')
    customer_id = fields.Many2one('archives.customer', string=u'客户名称', required=True)
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    saleType_id = fields.Many2one('archives.sale_type', string=u'销售类型', required=True)
    remark = fields.Char(string=u'摘要')

    sale_forecast_detail = fields.One2many('jc_sale.sale_forecast.detail', 'sale_forecast_id', string=u'销售预报明细',
                                           copy=True)

    company_id = fields.Many2one('archives.company', string=u'公司')
    staff_id = fields.Many2one('archives.staff', related='customer_id.staff_id', string=u'销售员', required=True)
    store_id = fields.Many2one('archives.store', string=u'仓库')

    @api.multi
    def add_goods_page(self):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('archives.archives_common_goods_action_page')
        list_view_id = imd.xmlid_to_res_id('archives.archives_common_goods_list')
        form_view_id = imd.xmlid_to_res_id('archives.archives_common_goods_edit')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            # 'context': action.context,
            'context': {
                'id': self.id,
                'customer_id': self.customer_id.id,
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
            'saleType_id': self.saleType_id.id,
            'staff_id': self.staff_id.id,
            'remark': self.remark,
        }
        order = self.env['jc_sale.sale_order'].create(values)
        for detail in self.sale_forecast_detail:
            values = {
                'sale_order_id': order.id,
                'forecast_id': self.id,
                'forecast_detail_id': detail.id,
                'goods_id': detail.goods_id.id,
                'secondUnit_id': detail.secondUnit_id.id,
                'secondUnitNumber': detail.secondUnitNumber,
                'mainUnit_id': detail.mainUnit_id.id,
                'mainUnitNumber': detail.mainUnitNumber,
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

    @api.multi
    def unlink(self):
        if self.bill_state > 1:
            raise ValidationError(_('只有未审核的单据才能审核.'))
        return super(SaleForecast, self).unlink()

    @api.multi
    def write(self, values):
        if self.bill_state > 1 and not SaleForecast._is_bill_state_change(values):
            raise ValidationError(_('只有未审核单据才能编辑.'))
        return super(SaleForecast, self).write(values)

    @api.multi
    def do_check(self):
        self.bill_state = 10
        self._create_order()

    @api.multi
    def do_finish(self):
        self.bill_state = 20

    @api.multi
    def do_un_finish(self):
        self.bill_state = 10

    @api.multi
    def do_un_check(self):
        self.bill_state = 1
        self._delete_order()


class SaleForecastDetail(models.Model):
    _name = 'jc_sale.sale_forecast.detail'

    sale_forecast_id = fields.Many2one('jc_sale.sale_forecast', string='销售预报引用', required=True,
                                       ondelete='cascade', index=True,
                                       copy=False)

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True)
    secondUnit_id = fields.Many2one('archives.unit', string=u'辅单位', compute='_set_second')
    secondUnitNumber = fields.Float(digits=(6, 2), string=u'辅数量')
    mainUnit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main')
    mainUnitNumber = fields.Float(digits=(6, 2), string=u'主数量')

    price = fields.Float(digits=(6, 2), help="单价", string=u'单价')
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额', compute='_compute_money')

    remark = fields.Char(string=u'备注')

    @api.depends('goods_id')
    def _set_main(self):
        for record in self:
            record.mainUnit_id = record.goods_id.mainUnit_id

    @api.depends('goods_id')
    def _set_second(self):
        for record in self:
            record.secondUnit_id = record.goods_id.secondUnit_id

    @api.depends('price', 'mainUnitNumber')
    def _compute_money(self):
        for record in self:
            record.money = record.price * record.mainUnitNumber

    @api.onchange('price', 'mainUnitNumber')
    def _onchange_for_money(self):
        self.money = self.price * self.mainUnitNumber

    @api.onchange('secondUnitNumber')
    def _onchange_second(self):
        if not self.goods_id.needSecondChange:
            return
        if self.goods_id.secondRate != 0:
            self.mainUnitNumber = self.goods_id.secondRate * self.secondUnitNumber

    @api.onchange('mainUnitNumber')
    def _onchange_main(self):
        if not self.goods_id.needSecondChange:
            return
        if self.goods_id.secondRate != 0:
            self.secondUnitNumber = self.mainUnitNumber / self.goods_id.secondRate

    @api.onchange('goods_id')
    def _onchange_goods(self):
        # self.secondUnit_id = self.env['archives.goods'].secondUnit_id
        # self.mainUnit_id = self.env['archives.goods'].mainUnit_id
        self.secondUnit_id = self.goods_id.secondUnit_id
        self.mainUnit_id = self.goods_id.mainUnit_id
