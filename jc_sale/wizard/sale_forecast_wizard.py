# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class SaleForecastWizard(models.Model):
    _name = 'jc_sale.forecast_multiple_add'

    name = fields.Char('名称')
    spell = fields.Char('首拼')

    lines = fields.One2many('jc_sale.forecast_multiple_add_detail', 'wizard_id', string='Products')

    def item_search(self):
        domain = []
        if self.name:
            domain += [('name', 'ilike', self.name)]
        if self.spell:
            domain += [('spell', 'ilike', self.spell)]
        items = self.env['archives.goods'].search(domain)
        wizard = self.create({})
        for product_id in items:
            val = {
                'main_unit_number': 0,
                'goods_id': product_id.id or False,
                'price': None,
                'main_unit_id': product_id.main_unit_id.id,
                'second_unit_id': product_id.second_unit_id.id,
                'wizard_id': wizard.id,
            }
            self.env['jc_sale.forecast_multiple_add_detail'].create(val)

        return {
            'name': '产品添加',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': wizard.id,
            'res_model': 'jc_sale.forecast_multiple_add',
            'type': 'ir.actions.act_window',
            'context': {'sale_id': self._context['active_id']}
        }

    def add_line(self):
        if not self.lines:
            return
        sale_id = self._context['sale_id']
        for line in self.lines:
            if line.selected:
                val = {
                    'goods_id': line.goods_id.id,
                    'main_unit_number': line.main_unit_number,
                    'sale_forecast_id': sale_id,
                    'price': line.price,
                }
                self.env['jc_sale.sale_forecast.detail'].create(val)
        self.env['jc_sale.forecast_multiple_add_detail'].search([]).unlink()
        self.env['jc_sale.forecast_multiple_add'].search([]).unlink()


class SaleForecastWizardDetail(models.Model):
    _name = 'jc_sale.forecast_multiple_add_detail'

    wizard_id = fields.Many2one('jc_sale.forecast_multiple_add', 'id')
    selected = fields.Boolean(string='添加？', store=True)
    goods_id = fields.Many2one('archives.goods', string=u'产品', required=True,
                               domain=lambda self: self.env['archives.organization'].get_goods_organization())
    price = fields.Float(digits=(6, 2), help="单价", string=u'单价')
    main_unit_id = fields.Many2one('archives.unit', string=u'主单位')
    second_unit_id = fields.Many2one('archives.unit', string=u'辅单位')
    main_unit_number = fields.Float(digits=(6, 2), string=u'主数量')
    money = fields.Float(digits=(6, 2), help="金额", string=u'金额', store=True, compute='_compute_amount')

    @api.depends('main_unit_number', 'price')
    def _compute_amount(self):
        for line in self:
            selected = True if line.main_unit_number > 0 else False
            line.update({
                'money': line.main_unit_number * line.price,
                'selected': selected,
            })
