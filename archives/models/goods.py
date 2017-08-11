# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Goods(models.Model):
    _name = 'archives.goods'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名物料"),
    ]

    name = fields.Char(string=u'物料名称', required=True)
    shortName= fields.Char(string=u'简称')

    # 通用信息
    mainUnit_id=fields.Many2one('archives.unit',string=u'主单位')
    secondUnit_id=fields.Many2one('archives.unit',string=u'辅单位')
    statisticsUnit_id=fields.Many2one('archives.unit',string=u'统计单位')

    secondRate=fields.Float(digits=(6, 2),string=u'辅单位转换率', help=u"主单位与辅单位的换算率，如“10”，一件（辅单位）=10公斤（主单位）" ,compute='_compute_second_rate')
    secondRateString=fields.Char(string=u'辅单位转换率')
    statisticsRate=fields.Float(digits=(6,2),string=u'统计单位转换率',help=u"主单位与统计单位的换算率，如“10”，一件（统计单位）=10公斤（主单位）",compute='_compute_statistics_rate')
    statisticsRateString=fields.Char(string=u'统计单位转换率')
    needSecondChange=fields.Selection([
        ('1', '是'),
        ('0', '否')
    ],string=u'辅单位是否换算',default='1')

    # 物料分类
    goodsType_id=fields.Many2one('archives.goods_type',string=u'物料分类')
    goodsType1_id = fields.Many2one('archives.goods_type1', string=u'物料分类1')
    goodsType2_id = fields.Many2one('archives.goods_type2', string=u'物料分类2')
    goodsType3_id = fields.Many2one('archives.goods_type3', string=u'物料分类3')
    goodsType4_id = fields.Many2one('archives.goods_type4', string=u'物料分类4')
    goodsType5_id = fields.Many2one('archives.goods_type5', string=u'物料分类5')
    goodsType6_id = fields.Many2one('archives.goods_type6', string=u'物料分类6')

    # 系统信息
    isSale=fields.Boolean(string=u'用于销售')
    isPurchase=fields.Boolean(string=u'用于采购')

    @api.depends('secondRateString')
    def _compute_second_rate(self):
        for record in self:
            record.secondRate=float(record.secondRateString)

    @api.depends('statisticsRateString')
    def _compute_statistics_rate(self):
        for record in self:
            record.statisticsRate=float(record.statisticsRateString)


    #     value = fields.Integer()
    #     value2 = fields.Float(compute="_value_pc", store=True)
    #     description = fields.Text()
    #
    #     @api.depends('value')
    #     def _value_pc(self):
    #         self.value2 = float(self.value) / 100