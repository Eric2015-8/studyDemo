# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleForecast(models.Model):
    _name = 'jc_sale.sale_forecast'
    #    _sql_constraints = [
    #        ('name_unique',
    #         'UNIQUE(name)',
    #         "已存在相同销售预报"),
    #    ]

    # name = fields.Char(string=u'销售预报', required=True, help=u'')
    customer_id = fields.Many2one('archives.customer', string=u'客户名称', required=True)
    date = fields.Date(string=u'日期', required=True, default=fields.Date.today)
    saleType_id = fields.Many2one('archives.sale_type', string=u'销售类型', required=True)
    remark = fields.Char(string=u'摘要')

    sale_forecast_detail = fields.One2many('jc_sale.sale_forecast.detail', 'sale_forecast_id', string=u'销售预报明细',
                                           copy=True)

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
    secondUnit_id = fields.Many2one('archives.unit', string=u'辅单位')
    secondUnitNumber = fields.Float(digits=(6, 2), string=u'辅数量')
    mainUnit_id = fields.Many2one('archives.unit', string=u'主单位')
    mainUnitNumber = fields.Float(digits=(6, 2), string=u'主数量')

    price = fields.Float(digits=(6, 2), help="单价", string=u'单价')
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额')

    remark = fields.Char(string=u'备注')

    @api.onchange('price', 'mainUnitNumber')
    def _onchange_unit(self):
        self.money = self.price * self.mainUnitNumber
        return {
            'warning': {
                'title': "Something bad happened",
                'message': "It was very bad indeed",
            }
        }
