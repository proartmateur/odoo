# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    html_color = fields.Char(string='Color',
                             help="Here you can set a specific HTML color index (e.g. #ff0000) to display the color if the attribute type is 'Color'.")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    html_color = fields.Char(string='Color', related="categ_id.html_color")
