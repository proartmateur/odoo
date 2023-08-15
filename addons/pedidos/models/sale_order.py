from odoo import api, fields, models, _
from odoo.tests import  Form

class SaleOrder(models.Model):
     _inherit = "sale.order"
     
     pedidos_id=fields.Many2one('request.pedidos',string="Pedidos Id")
     etapa = fields.Selection(related="pedidos_id.etapa")
     fecha =fields.Date(related='pedidos_id.date',string='Fecha')

     # def action_confirm(self):
     #    res = super(SaleOrder, self).action_confirm()
     #    for order in self:
     #        for piking in order.picking_ids:
     #            for pk in piking.move_ids_without_package:
     #                pk.write({'quantity_done':pk.product_uom_qty})
     #            res_dict = piking.button_validate()
                
     #            #res = outgoing_shipment.button_validate()
     #            # print("AAAAAAAAAAAAAAAAAAA",res_dict)
     #            # Form(self.env['stock.immediate.transfer'].with_context(res_dict['context'])).save().process()
     #            order.pedidos_id.etapa = 'En preparación'
     #    return res

     def _compute_invoice_status(self):
        super()._compute_invoice_status()
        for order in self:
            if order.pos_order_count > 0 and order.state == 'sale':
                if order.pedidos_id:
                    self.pedidos_id.etapa = 'finalizado'


     @api.onchange('etapa')
     def _onchange_pedidos_epta(self):
         self.ensure_one()
         for order in self:
             if order.pedidos_id and order.etapa:
                order.pedidos_id.etapa=order.etapa