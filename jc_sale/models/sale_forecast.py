# -*- coding: utf-8 -*-

from odoo import models, fields, api  # , _


class SaleForecast(models.Model):
    _name = 'jc_sale.sale_forecast'

    # name = fields.Char(string=u'销售预报', required=True, help=u'')
    customer_id = fields.Many2one('archives.customer', string=u'客户名称', required=True)
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    saleType_id = fields.Many2one('archives.sale_type', string=u'销售类型', required=True)
    remark = fields.Char(string=u'摘要')

    sale_forecast_detail = fields.One2many('jc_sale.sale_forecast.detail', 'sale_forecast_id', string=u'销售预报明细',
                                           copy=True)

    company_id = fields.Many2one('archives.company', string=u'公司')
    staff_id = fields.Many2one('archives.staff', string=u'销售员', required=True)
    store_id = fields.Many2one('archives.store', string=u'仓库')

    #     value = fields.Integer()
    #     value2 = fields.Float(compute="_value_pc", store=True)
    #     description = fields.Text()
    #
    #     @api.depends('value')
    #     def _value_pc(self):
    #         self.value2 = float(self.value) / 100


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
        if  self.goods_id.secondRate != 0:
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
