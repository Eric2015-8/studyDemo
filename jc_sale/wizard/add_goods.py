# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AddGoods(models.TransientModel):
    _name = 'jc_sale.add_goods'

    # add_goods_detail = fields.One2many('jc_sale.add_goods.detail', 'add_goods_id', string=u'销售预报明细', copy=True)
    goods_ids = fields.Many2many('archives.goods', string=u'产品')


class AddGoodsDetail(models.TransientModel):
    _name = 'jc_sale.add_goods.detail'
    # def _default_sessions(self):
    #     return self.env['openacademy.session'].browse(self._context.get('active_ids'))

    add_goods_id = fields.Many2one('jc_sale.add_goods', string='销售预报引用', required=True,
                                   ondelete='cascade', index=True, copy=False)

    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True)
    secondUnit_id = fields.Many2one('archives.unit', string=u'辅单位', compute='_set_second')
    secondUnitNumber = fields.Float(digits=(6, 2), string=u'辅数量')
    mainUnit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main')
    mainUnitNumber = fields.Float(digits=(6, 2), string=u'主数量')

    @api.multi
    def subscribe(self):
        # for session in self.session_ids:
        #     session.attendee_ids |= self.attendee_ids
        return {}

    # @api.depends('goods_id')
    # def _set_main(self):
    #     for record in self:
    #         record.mainUnit_id = record.goods_id.mainUnit_id
    #
    # @api.depends('goods_id')
    # def _set_second(self):
    #     for record in self:
    #         record.secondUnit_id = record.goods_id.secondUnit_id
    #
    # @api.onchange('secondUnitNumber')
    # def _onchange_second(self):
    #     if not self.goods_id.needSecondChange:
    #         return
    #     if self.goods_id.secondRate != 0:
    #         self.mainUnitNumber = self.goods_id.secondRate * self.secondUnitNumber
    #
    # @api.onchange('mainUnitNumber')
    # def _onchange_main(self):
    #     if not self.goods_id.needSecondChange:
    #         return
    #     if self.goods_id.secondRate != 0:
    #         self.secondUnitNumber = self.mainUnitNumber / self.goods_id.secondRate
    #
    # @api.onchange('goods_id')
    # def _onchange_goods(self):
    #     self.secondUnit_id = self.goods_id.secondUnit_id
    #     self.mainUnit_id = self.goods_id.mainUnit_id

        # session_ids = fields.Many2many('openacademy.session',
        #                                string="Sessions", required=True, default=_default_sessions)
        # attendee_ids = fields.Many2many('res.partner', string="Attendees")
        #
        # @api.multi
        # def subscribe(self):
        #     for session in self.session_ids:
        #         session.attendee_ids |= self.attendee_ids
        #     return {}
