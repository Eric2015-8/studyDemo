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
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位', compute='_set_second')
    second_unit_number = fields.Float(digits=(6, 2), string=u'辅数量')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位', compute='_set_main')
    main_unit_number = fields.Float(digits=(6, 2), string=u'主数量')

    @api.multi
    def subscribe(self):
        # for session in self.session_ids:
        #     session.attendee_ids |= self.attendee_ids
        return {}

    # @api.depends('goods_id')
    # def _set_main(self):
    #     for record in self:
    #         record.main_unit_id = record.goods_id.main_unit_id
    #
    # @api.depends('goods_id')
    # def _set_second(self):
    #     for record in self:
    #         record.second_unit_id = record.goods_id.second_unit_id
    #
    # @api.onchange('second_unit_number')
    # def _onchange_second(self):
    #     if not self.goods_id.need_second_change:
    #         return
    #     if self.goods_id.second_rate != 0:
    #         self.main_unit_number = self.goods_id.second_rate * self.second_unit_number
    #
    # @api.onchange('main_unit_number')
    # def _onchange_main(self):
    #     if not self.goods_id.need_second_change:
    #         return
    #     if self.goods_id.second_rate != 0:
    #         self.second_unit_number = self.main_unit_number / self.goods_id.second_rate
    #
    # @api.onchange('goods_id')
    # def _onchange_goods(self):
    #     self.second_unit_id = self.goods_id.second_unit_id
    #     self.main_unit_id = self.goods_id.main_unit_id

        # session_ids = fields.Many2many('openacademy.session',
        #                                string="Sessions", required=True, default=_default_sessions)
        # attendee_ids = fields.Many2many('res.partner', string="Attendees")
        #
        # @api.multi
        # def subscribe(self):
        #     for session in self.session_ids:
        #         session.attendee_ids |= self.attendee_ids
        #     return {}
