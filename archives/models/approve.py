# -*- coding: utf-8 -*-
from odoo import models


class Approve(models.AbstractModel):
    """
    审批的基类，用于取消对审批模块的依赖
    """
    _name = 'jc_approve'
