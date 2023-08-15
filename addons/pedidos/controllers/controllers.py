# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, http, fields
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv import expression
from odoo.tools import float_round, float_repr

def get_pricelistpriceproduct(partner_id,product_id,quantity,order_date,currency_id):
        if partner_id.property_product_pricelist.item_ids:
            pricelist_rule = partner_id.property_product_pricelist.item_ids[0]
        else:
            pricelist_rule = False

        item_ids = partner_id.property_product_pricelist._get_product_rule(
                    product_id,
                    1.0,
                    uom=product_id.uom_id,
                    date=order_date,
                )

        if item_ids and pricelist_rule:
            order_date = order_date
            product = product_id
            qty = 1.0
            uom = product_id.uom_id
            price = pricelist_rule._compute_price(
                product, qty, uom, order_date, currency=currency_id)
        else:
            price = product_id.list_price

        return price * quantity

class PedidosController(http.Controller):
    @http.route('/pedidos/infos', type='json', auth='user')
    def infospedidos(self, user_id=None,employee_id=None,config_id=None,note=None,expected_delivered_date=None):
        self._check_user_impersonification(user_id)
        user = request.env['res.users'].browse(user_id) if user_id else request.env.user
        employee=False
        if employee_id:
            employee=request.env['res.partner'].browse(employee_id)

        config=False
        if config_id:
            config=request.env['pos.config'].browse(config_id)

        infos = self._make_infos(user,employee,config,order=False)

        lines = self._get_current_lines(user)
        for li in lines:
            if employee:
                price=get_pricelistpriceproduct(employee,li.product_id,li.quantity,li.date,li.currency_id)
                price = li.product_id.taxes_id.compute_all(price, product=li.product_id, partner=employee)
                price=price['total_included']
                li.update({'price':price})
                
        if lines:
            translated_states = dict(request.env['product.order']._fields['state']._description_selection(request.env))

            lines = [{'id': line.id,
                      'product': (line.product_id.id, line.product_id.name, float_repr(float_round(line.price, 2), 2)),
                      'quantity': line.quantity,
                      'price': line.price ,
                      'raw_state': line.state,
                      'state': translated_states[line.state],
                      'uom':line.product_id.uom_id.name,
                      'note': line.note} for line in lines.sorted('date')]

            lines.reverse()
            
            # if lines:
            #     note=note
            # else:
            #     note=''
            infos.update({
                'total': float_repr(float_round(sum(line['price'] for line in lines), 2), 2),
                'raw_state': self._get_state(lines),
                'lines': lines,
                'note':note,
                'expected_delivered_date':expected_delivered_date,
                'date':fields.Date.context_today(user)
            })
        # else:
        #     note=''
        return infos

    @http.route('/pedidos/trash', type='json', auth='user')
    def Pedidostrash(self, user_id=None):
        self._check_user_impersonification(user_id)
        user = request.env['res.users'].browse(user_id) if user_id else request.env.user

        lines = self._get_current_lines(user)
        lines = lines.filtered_domain([('state', 'not in', ['sent', 'confirmed'])])
        lines.action_cancel()
        lines.unlink()


    @http.route('/add/product/pedidios', type='json', auth='user')
    def Addproductorde(self, productId,Qty,Note):
        partner_id=False
        config_id=False
        if request.env.context.get('default_empoyee_id'):
            partner_id=request.env.context.get('default_empoyee_id')
        else:
            partner_id=request.env.user.partner_id.id

        if request.env.context.get('default_config_id'):
            config_id=request.env.context.get('default_config_id')

        request.env['product.order'].create({'product_id':productId,'quantity':Qty,'note':Note,'partner_id':partner_id,'pos_config_id':config_id})
        return True

    @http.route('/pedidos/pay', type='json', auth='user')
    def Pedidospay(self, user_id=None,employee_id=None,config_id=None,note=None,expected_delivered_date=None):
        self._check_user_impersonification(user_id)
        user = request.env['res.users'].browse(user_id) if user_id else request.env.user

        lines = self._get_current_lines(user)
        if lines:
            lines = lines.filtered(lambda line: line.state == 'new')

            lines.action_order(note,expected_delivered_date)
            return True

        return False

    def _make_infos(self, user, employee,config,**kwargs):
        res = dict(kwargs)
        currency = user.company_id.currency_id
        employee_value=''
        config_value=''
        if employee:
            employee_value=employee.sudo().name

        if config:
            config_value=config.sudo().name
        res.update({
            'username': user.sudo().name,
            'date':fields.Date.context_today(user),
            'employename':employee_value,
            'placeholder':'sss',
            'configname':config_value,
            'userimage': '/web/image?model=res.users&id=%s&field=avatar_128' % user.id,
            'is_manager': True,
            'group_portal_id': request.env.ref('base.group_portal').id,
            'currency': {'symbol': currency.symbol, 'position': currency.position},
            'alerts':[]
        })

        return res

    def _check_user_impersonification(self, user_id=None):
        if (user_id and request.env.uid != user_id):
            raise AccessError(_('You are trying to impersonate another user, but this can only be done by a manager'))

    def _get_current_lines(self, user):
        return request.env['product.order'].search(
            [('user_id', '=', user.id), ('date', '=', fields.Date.context_today(user)), ('state', '!=', 'cancelled')]
            )

    def _get_state(self, lines):
        """
            This method returns the lowest state of the list of lines

            eg: [confirmed, confirmed, new] will return ('new', 'To Order')
        """
        states_to_int = {'new': 0, 'ordered': 1, 'sent': 2, 'confirmed': 3, 'cancelled': 4}
        int_to_states = ['new', 'ordered', 'sent', 'confirmed', 'cancelled']

        return int_to_states[min(states_to_int[line['raw_state']] for line in lines)]
