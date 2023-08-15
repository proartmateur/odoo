# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    user_id = fields.Many2one('hr.employee', string='Salesperson')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_commissionable=fields.Boolean('Is Commissionable')

# class ProductProduct(models.Model):
#     _inherit = "product.product"

#     is_commissionable=fields.Boolean('Is Commissionable')    
#product.product

class SaleOrder(models.Model):
     _inherit = "sale.order"
     
     is_for_pos=fields.Boolean('Is For POS?')
     pos_config_ids = fields.Many2one("pos.config", string="Point of Sales")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_sale_order_fields(self):
        field_names = super()._get_sale_order_fields()
        field_names.append('set_employee')
        return field_names

    set_employee=fields.Many2one('hr.employee',string='Salesperson')

    # def _get_sale_order_fields(self):
    #     field_names = super()._get_sale_order_fields()
        
    #     field_names.append('set_employee')
    #     return field_names


class Employee(models.Model):
    _inherit = 'hr.employee'

    is_sale_person=fields.Boolean('Is Sales Person')


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('is_commissionable')
        return result
    
    def _loader_params_hr_employee(self):
        result = super()._loader_params_hr_employee()
        result['search_params']['fields'].append('is_sale_person')
        return result