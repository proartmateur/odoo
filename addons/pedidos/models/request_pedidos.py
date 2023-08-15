from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from collections import defaultdict

class RequestPedidos(models.Model):
    _name = 'request.pedidos'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Request Pedidos'
    _order = 'id desc'
    _display_name = 'name'


    name=fields.Char("Name")
    partner_id=fields.Many2one('res.partner',string='Contact')
    phone=fields.Char('Phone',related='partner_id.phone')
    email=fields.Char('Email',related='partner_id.email')
    date = fields.Date('Fecha', required=True, readonly=True,default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', 'User', readonly=True,default=lambda self: self.env.uid)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency',related='company_id.currency_id', store=True)
    #pricelist_id=fields.Many2one('product.pricelist',string='Pricelist')
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True, required=True,
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    order_line_ids=fields.One2many('request.pedidos.line','pedidos_id',string='Pedidos Lines')
    pos_config_ids = fields.Many2one("pos.config", string="Point of Sales")
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts', tracking=4)
    order_ids=fields.One2many('sale.order','pedidos_id',string='Order Id')
    order_count = fields.Integer(compute='_compute_order_count')
    note=fields.Char('Note')
    expected_delivered_date=fields.Datetime('Expected Delivered Date')
    sale_amt_total = fields.Monetary(string="Sale Amt", compute='_compute_sale_amounts')
    sum_of_kg = fields.Float(string="Sum of KG", compute='_compute_sum_of_kg')
    sum_of_unit = fields.Float(string="Sum of UNIT", compute='_compute_sum_of_unit')
    etapa = fields.Selection(
        [('new','NEW'),
         ('Nuevo', 'En proceso'),
         ('En preparación', 'Listo'),
         ('finalizado','Finalizado')],
        string='Etapa')
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='_compute_fiscal_position_id',
        store=True, readonly=False, precompute=True, check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
            "The default value comes from the customer.",
        domain="[('company_id', '=', company_id)]")
    state = fields.Selection([
        ('new', 'New'),
        ('approve', 'Approve'),], default='new' ,string='State')

    def approve_pedido(self):
        self.state='approve'



    @api.depends('partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        cache = {}
        for order in self:
            if not order.partner_id:
                order.fiscal_position_id = False
                continue
            key = (order.company_id.id, order.partner_id.id)
            if key not in cache:
                cache[key] = self.env['account.fiscal.position'].with_company(
                    order.company_id
                )._get_fiscal_position(order.partner_id)
            order.fiscal_position_id = cache[key]

    def write(self, vals):
        if 'pos_config_ids' in vals:
            if self.pos_config_ids:
                self.message_post(body=_(
                    "Point Of Sale is Changed  %s. To %s.",
                    self.pos_config_ids._get_html_link(),
                    self.env['pos.config'].search([('id','=',vals.get('pos_config_ids'))])._get_html_link(),
                ))
            else:
                self.message_post(body=_(
                    "Point Of Sale is Added  %s.",
                    self.env['pos.config'].search([('id','=',vals.get('pos_config_ids'))])._get_html_link(),
                ))

        
        return super(RequestPedidos, self).write(vals)

    def _compute_order_count(self):
        orders_data = self.env['sale.order'].search([('pedidos_id', 'in', self.ids)])
        self.order_count = len(orders_data)

    def _compute_sale_amounts(self):
        for rec in self:
            orders_data = self.env['sale.order'].search([('pedidos_id', '=', rec.id)])
            total = 0.0
            for order in orders_data:
                total += order.amount_total
            rec.sale_amt_total = total

    def _compute_sum_of_kg(self):
        for order in self:
            count_kg = 0.0
            for line in order.order_line_ids:
                if line.product_id.uom_id.name == 'kg':
                    count_kg += 1
            order.sum_of_kg = count_kg

    def _compute_sum_of_unit(self):
        count_unit = 0.0
        for order in self:
            for line in order.order_line_ids:
                if line.product_id.uom_id.name == 'Units' or line.product_id.uom_id.name == 'units':
                    count_unit += 1
            order.sum_of_unit = count_unit

    def action_view_order(self):
        self.ensure_one()
        #linked_orders = self.lines.mapped('sale_order_origin_id')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Orders'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('pedidos_id', 'in', self.ids)],
        }


    @api.depends('order_line_ids.price_subtotal')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            order_lines = order.order_line_ids
            order.amount_total = sum(order_lines.mapped('price_subtotal'))

    def create_sale_order(self):
        for order in self:
            data={}
            data['partner_id']=order.partner_id.id
            data['pricelist_id']=order.pricelist_id.id
            data['pedidos_id']=self.id
            data['note']=order.note
            #data['etapa']=order.etapa
            sale_lines=[]
            for line in order.order_line_ids:
                sale_lines.append((0, 0, {
                'name' : line.note or line.product_id.name,
                'product_id' : line.product_id.id,
                'product_uom' : line.product_id.uom_id.id,
                'product_uom_qty' :line.product_uom_qty,
                
              }))
            data['order_line']=sale_lines
            if order.pos_config_ids:
                data['is_for_pos']=True
                data['pos_config_ids']=order.pos_config_ids.id
            
            sale_order=self.env['sale.order'].create(data)
            order.etapa='Nuevo'
            #sale_order.write({'order_line_ids' : sale_lines})

    

    @api.depends('partner_id')
    def _compute_pricelist_id(self):
        for order in self:
            if not order.partner_id:
                order.pricelist_id = False
                continue
            order = order.with_company(order.company_id)
            order.pricelist_id = order.partner_id.property_product_pricelist
            for line in order.order_line_ids:
                line.update({'price':line.get_pricelistprice_pedidos()})

    @api.onchange('etapa')
    def _onchange_saleorder_epta(self):
        self.ensure_one()
        for order in self:
            if order.order_ids and order.etapa:
                for sale in order.order_ids:
                    sale_id=str(sale.id)
                    if 'NewId_' in sale_id:
                        sale_id=sale_id.replace("NewId_", "")
                    sale_order=self.env['sale.order'].browse(int(sale_id))
                    sale_order.write({'etapa':order.etapa})
                    #sale.write({'etapa':order.etapa})

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id_update_prices(self):
        for order in self:
            if order.pricelist_id:
                # order.message_post(body=_(
                #     "Product prices have been recomputed according to pricelist %s.",
                #     order.pricelist_id.name,
                # ))
                # order.activity_schedule(
                #     'mail.mail_activity_data_warning',
                #     user_id=order.user_id.id,
                #     note=_(
                #         "Product prices have been recomputed according to pricelist %s.",
                #         order.pricelist_id.name,
                #     )
                # )
                for line in order.order_line_ids:
                    line.update({'price':line.get_pricelistprice_pedidos()})
        

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('pedidos.request') or _('New')
        return super().create(vals_list)
    
class RequestPedidosLine(models.Model):
    _name = 'request.pedidos.line'
    _description = 'Request Pedidos Line'
    _order = 'id desc'
    _display_name = 'name'

    name=fields.Char('Description')
    product_id=fields.Many2one('product.product', string="Product", required=True)
    product_uom=fields.Many2one('uom.uom',string='Product UOM')
    product_uom_qty=fields.Float('Quantity',store=True)
    price=fields.Float('Price')
    unit_price=fields.Float('Unit Price')
    price_subtotal=fields.Float('Sub Total',compute='_compute_amount',
        store=True, precompute=True)
    pedidos_id=fields.Many2one('request.pedidos')
    partner_id=fields.Many2one('res.partner',related='pedidos_id.partner_id',string='Contact')
    date = fields.Date('Fecha',related='pedidos_id.date')
    note=fields.Char('Note')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency',related='company_id.currency_id', store=True)
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        related='pedidos_id.pricelist_id')
    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_id',
        store=True, readonly=False, precompute=True,
        context={'active_test': False})

    @api.depends('product_id')
    def _compute_tax_id(self):
        taxes_by_product_company = defaultdict(lambda: self.env['account.tax'])
        lines_by_company = defaultdict(lambda: self.env['request.pedidos.line'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for product in self.product_id:
            for tax in product.taxes_id:
                taxes_by_product_company[(product, tax.company_id)] += tax
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = taxes_by_product_company[(line.product_id, company)]
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_id = False
                    continue
                fiscal_position = line.pedidos_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_id = result

    @api.depends('product_uom_qty','price')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            #amount_sub=line.product_uom_qty * line.price
            line.update({
                'price_subtotal': line.price, 
            })

    def get_pricelistprice_pedidos(self):
        for line in self:
            pricelist_rule = line.pricelist_id.item_ids
            item_ids = line.pricelist_id._get_product_rule(
                        line.product_id,
                        1.0,
                        uom=line.product_id.uom_id,
                        date=line.date or fields.Date.today(),
                    )

            if item_ids:
                order_date = line.date or fields.Date.today()
                product = line.product_id
                qty = 1.0
                uom = line.product_id.uom_id
                price = pricelist_rule._compute_price(
                    product, qty, uom, order_date, currency=line.currency_id)
            else:
                price = line.product_id.list_price

            return price