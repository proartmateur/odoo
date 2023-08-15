odoo.define('pw_pos_restrict_refund.TicketScreen', function (require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');

    const { _t } = require('web.core');

    const PWTicketScreen = (TicketScreen) =>
        class extends TicketScreen {
            async _onDoRefund() {
                if(this.env.pos.config.pw_refund_employee_ids) {
                    var get_config_emp=this.env.pos.employees.filter((employee) => employee.id == this.env.pos.config.pw_refund_employee_ids[0])
                    if(get_config_emp[0].pin){
                        const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                            isPassword: true,
                            title: this.env._t('Password ?'),
                            startingValue: null,
                        });
                        if (!confirmed) return;
                      
                        if (Sha1.hash(inputPin) === get_config_emp[0].pin) {
                            super._onDoRefund()
                        } else {
                            await this.showPopup('ErrorPopup', {
                                title: this.env._t('Incorrect Password'),
                            });
                            return;
                        }
                    }else{
                        super._onDoRefund()
                    }
                }
                else {
                    super._onDoRefund()
                }
            }
            _onCreateNewOrder() {
                var get_lenght=this.getFilteredOrderList()
                if(get_lenght.length < 2){
                    this.env.pos.add_new_order();
                    this.showScreen('ProductScreen');
                }else{
                 this.showPopup('ErrorPopup', {
                                title: this.env._t("You Can't Do More Than Two Orders"),
                            });
                }
                
            }
            async _onDeleteOrder() {
                if(this.env.pos.config.pw_refund_employee_ids) {
                    var get_config_emp=this.env.pos.employees.filter((employee) => employee.id == this.env.pos.config.pw_refund_employee_ids[0])
                    if(get_config_emp[0].pin){
                        const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                            isPassword: true,
                            title: this.env._t('Password ?'),
                            startingValue: null,
                        });
                        if (!confirmed) return;
                        if (Sha1.hash(inputPin) === get_config_emp[0].pin) {
                            await super._onDeleteOrder(...arguments);
                        } else {
                            await this.showPopup('ErrorPopup', {
                                title: this.env._t('Incorrect Password'),
                            });
                            return;
                        }
                    }else{
                        await super._onDeleteOrder(...arguments);
                    }
                }
                else {
                    await super._onDeleteOrder(...arguments);
                }

            }
        };

    Registries.Component.extend(TicketScreen, PWTicketScreen);

    return TicketScreen;
});
