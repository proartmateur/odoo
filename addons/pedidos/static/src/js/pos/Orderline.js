odoo.define('pedidos.Orderline', function (require) {
    'use strict';

    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');

    const PedidosOrderline = (Orderline) =>
        class extends Orderline {

            async selectLine() {
                if(!this.props.line.multiple_qty){
                    const { confirmed, payload: qty } = await this.showPopup('TextInputPopup', {
                        title: this.env._t(`Enter Multiple Qty`),
                        startingValue: this.props.line.multiple_qty || '',
                    });
                    if(confirmed){
                        this.props.line.set_multiple_qty(parseFloat(qty) || 0);
                    }
                }
                super.selectLine(...arguments);
            }
           
        };

    Registries.Component.extend(Orderline, PedidosOrderline);

    return Orderline;
});
