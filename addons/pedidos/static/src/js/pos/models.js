odoo.define('pedidos.models', function (require) {
    "use strict";

var { Orderline } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');
var core = require('web.core');
var { Gui } = require('point_of_sale.Gui');

var _t = core._t;

const PedidosOrderline = (Orderline) => class PedidosOrderline extends Orderline {
    async set_quantity(quantity, keep_price) {
        var self=this
        if(! quantity){
            if(self.pos.config.pw_refund_employee_ids) {
                var get_config_emp=self.pos.employees.filter((employee) => employee.id == self.pos.config.pw_refund_employee_ids[0])
                if(get_config_emp[0].pin){
                    const { confirmed, payload: inputPin } = await Gui.showPopup('NumberPopup', {
                        isPassword: true,
                        title: _t('Password ?'),
                        startingValue: null,
                    });
                    if (!confirmed) return;
                    
                    if (Sha1.hash(inputPin) === get_config_emp[0].pin) {
                        return super.set_quantity(...arguments);
                    } else {
                        await Gui.showPopup('ErrorPopup', {
                            title: _t('Incorrect Password'),
                        });
                        return;
                    }
                }else{
                    await Gui.showPopup('ErrorPopup', {
                        title: _t('Please Set PIN of Refund employee in setting'),
                    });
                    return;
                }
            }else{
                return super.set_quantity(...arguments);
            }
        }else{
            return super.set_quantity(...arguments);
        }
        
    }
}

Registries.Model.extend(Orderline, PedidosOrderline);

});