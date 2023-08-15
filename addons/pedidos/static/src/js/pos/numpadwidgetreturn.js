odoo.define('pedidos.numpadwidgetreturn', function (require) {
    'use strict';

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');

    const PedidosNumberreturn = (NumpadWidget) =>
        class extends NumpadWidget {
            async sendInput(key) {
                var self=this
                var selected_line=self.env.pos.get_order().get_selected_orderline()
                if(selected_line){
                    if(key == 'Backspace' && self.props.activeMode == "quantity"){
                        if(self.env.pos.config.pw_refund_employee_ids) {
                            var get_config_emp=this.env.pos.employees.filter((employee) => employee.id == this.env.pos.config.pw_refund_employee_ids[0])
                            if(get_config_emp[0].pin){
                                const { confirmed, payload: inputPin } = await self.showPopup('NumberPopup', {
                                    isPassword: true,
                                    title: self.env._t('Password ?'),
                                    startingValue: null,
                                });
                                if (!confirmed) return;
                                
                                if (Sha1.hash(inputPin) === get_config_emp[0].pin) {
                                    self.trigger('numpad-click-input', { key });
                                } else {
                                    await self.showPopup('ErrorPopup', {
                                        title: self.env._t('Incorrect Password'),
                                    });
                                    return;
                                }
                            }else{
                                await self.showPopup('ErrorPopup', {
                                    title: self.env._t('Please Set PIN of Refund employee in setting'),
                                });
                                return;
                            }
                        }else{
                            selected_line.quantity = 0;
                            self.trigger('numpad-click-input', { key });
                        }
                    }
                }
                else super.sendInput(...arguments);
            }
           
        };

    Registries.Component.extend(NumpadWidget, PedidosNumberreturn);

    return NumpadWidget;
});
