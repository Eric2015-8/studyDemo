# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Staff(models.Model):
    _name = 'archives.staff'
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "已存在同名员工"),
    ]

    name = fields.Char(string=u'员工姓名', required=True)

    #     public
    company_id = fields.Many2one('archives.company', string=u'公司', index=True)
    department_id = fields.Many2one('archives.department', string=u'部门')
    duty_id = fields.Many2one('archives.duty', string=u'职务')
    tel = fields.Char(string=u'手机')
    office_tel = fields.Char(string=u'办公电话')
    email = fields.Char()

    #     个人信息
    id_no = fields.Char(string=u'身份证号')
    address = fields.Char(string=u'家庭住址')
    account_id = fields.Many2one('archives.account', string=u'账号')
    birthday = fields.Date(string=u'出生日期')
    gender = fields.Selection([
        ('male', '男'),
        ('female', '女'),
        ('other', '其他')
    ], string=u'性别')
    place = fields.Char(string=u'籍贯')

    #     系统信息
    is_sale_man = fields.Boolean(string=u'销售员')
    is_purchase_man = fields.Boolean(string=u'采购员')
    is_driver = fields.Boolean(string=u'司机')
    is_sender = fields.Boolean(string=u'送货员')

    # value = fields.Integer()
    # value2 = fields.Float(compute="_value_pc", store=True)
    # description = fields.Text()
    #
    # @api.depends('value')
    # def _value_pc(self):
    #     self.value2 = float(self.value) / 100
