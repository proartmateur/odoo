# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    multiple_qty = fields.Float()

    @api.constrains('multiple_qty')
    def _constrains_multiple_qty(self):
        for rec in self:
            if rec.multiple_qty:
                rec.qty *= rec.multiple_qty or 1