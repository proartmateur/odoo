# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ProductOrder(models.Model):
    _name = 'product.order'
    _description = 'Product Order'
    _order = 'id desc'
    _display_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    name = fields.Char(related='product_id.name', string="Product Name", store=True, readonly=True)
    category_id = fields.Many2one('product.category',
        string='Product Category', related='product_id.categ_id', store=True)
    date = fields.Date('Order Date', required=True, readonly=True,
                       states={'new': [('readonly', False)]},
                       default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', 'User', readonly=True,
                              states={'new': [('readonly', False)]},
                              default=lambda self: self.env.uid)
    note = fields.Text('Notes')
    expected_delivered_date=fields.Datetime('Expected Delivered Date')
    price = fields.Monetary('Total Price', compute='_compute_total_price', readonly=True, store=True)
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([('new', 'To Order'),
                              ('ordered', 'Ordered'),       # "Internally" ordered
                              ('sent', 'Sent'),             # Order sent to the supplier
                              ('confirmed', 'Received'),    # Order received
                              ('cancelled', 'Cancelled')],
                             'Status', readonly=True, index=True, default='new')
    notified = fields.Boolean(default=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency',related='company_id.currency_id', store=True)
    quantity = fields.Float('Quantity', required=True, default=1)
    product_description = fields.Html('Description', related='product_id.description')

    image_1920 = fields.Image(compute='_compute_product_images')
    image_128 = fields.Image(compute='_compute_product_images')
    sale_order_id=fields.Many2one('sale.order',string='Sale Order')
    partner_id=fields.Many2one('res.partner',string='Partner')
    pos_config_id = fields.Many2one("pos.config", string="Point of Sales")

    @api.depends('product_id')
    def _compute_product_images(self):
        for line in self:
            line.image_1920 = line.product_id.image_1920
            line.image_128 = line.product_id.image_128


    @api.model_create_multi
    def create(self, vals_list):
        orders = self.env['product.order']
        for vals in vals_list:
            lines = self._find_matching_lines({
                **vals
            })
            if lines.filtered(lambda l: l.state not in ['sent', 'confirmed']):
                lines.update_quantity(1)
                orders |= lines[:1]
            else:
                orders |= super().create(vals)
        return orders

    @api.model
    def _find_matching_lines(self, values):
        domain = [
            ('user_id', '=', values.get('user_id', self.default_get(['user_id'])['user_id'])),
            ('product_id', '=', values.get('product_id', False)),
            ('date', '=', fields.Date.today()),
            ('note', '=', values.get('note', False)),
        ]
        return self.search(domain)

    def get_pricelistprice(self):
        if self.partner_id.property_product_pricelist.item_ids:
            pricelist_rule = self.partner_id.property_product_pricelist.item_ids[0]
        else:
            pricelist_rule=False
        item_ids = self.partner_id.property_product_pricelist._get_product_rule(
                    self.product_id,
                    1.0,
                    uom=self.product_id.uom_id,
                    date=self.date or fields.Date.today(),
                )

        if item_ids and pricelist_rule:
            order_date = self.date or fields.Date.today()
            product = self.product_id
            qty = 1.0
            uom = self.product_id.uom_id
            price = pricelist_rule._compute_price(
                product, qty, uom, order_date, currency=self.currency_id)
        else:
            price = self.product_id.list_price

        return price

    @api.depends('product_id', 'quantity')
    def _compute_total_price(self):
        for line in self:
            if line.product_id:
                line.price = line.quantity * line.get_pricelistprice()
   
    
    def update_quantity(self, increment):
        for line in self.filtered(lambda line: line.state not in ['sent', 'confirmed']):
            if increment == 0:
                line.active = False
            else:
                line.quantity = increment

    def update_note(self, note):
        for line in self.filtered(lambda line: line.state not in ['sent', 'confirmed']):
            line.note = note
        

    def add_to_cart(self):
        return True

    def action_order(self,note,date):
        if not date:
            date=fields.Date.context_today(self.user_id)

        sale_lines=[]
        sale_data={}
        partner_id=False
        config_id=False
        for order in self:
            partner_id=order.partner_id.id
            config_id=order.pos_config_id.id
            sale_lines.append((0, 0, {
                'name' : order.note,
                'product_id' : order.product_id.id,
                'product_uom' : order.product_id.uom_id.id,
                'product_uom_qty' :order.quantity,
                'price':order.price,
                'note':order.note
              }))
            
            self.write({
                'state': 'ordered'
            })
            order.unlink()

        if partner_id:
            sale_data['partner_id']=partner_id
            sale_data['pos_config_ids']=config_id
            sale_data['note']=note
            sale_data['date']=date
            sale_data['expected_delivered_date']=date
            sale_data['etapa']='new'
            sale_order=self.env['request.pedidos'].create(sale_data)
            sale_order.write({'order_line_ids' : sale_lines})

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'ordered'})

    def action_send(self):
        self.state = 'sent'
