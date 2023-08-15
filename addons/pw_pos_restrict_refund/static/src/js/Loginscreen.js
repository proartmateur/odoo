odoo.define('pw_pos_restrict_refund.Loginscreen', function (require) {
    'use strict';

    const LoginScreen = require('pos_hr.LoginScreen');
    const Registries = require('point_of_sale.Registries');
    //var rpc = require('web.rpc');

    const { _t } = require('web.core');

    const LoginScreencomissionist = (LoginScreen) =>
        class extends LoginScreen {
            async selectComissionist() {
                if (await this.selectCashiercomission()) {
                    this.back();
                }
            }
            async selectCashiercomission() {
                if (this.env.pos.config.module_pos_hr) {
                    const employeesList = this.env.pos.comissionists
                        .filter((employee) => employee.id !== this.env.pos.get_cashier().id)
                        .map((employee) => {
                            return {
                                id: employee.id,
                                item: employee,
                                label: employee.name,
                                isSelected: false,
                            };
                        });
                    let {confirmed, payload: employee} = await this.showPopup('SelectionPopup', {
                        title: this.env._t('Change Comissionists'),
                        list: employeesList
                    });

                    if (!confirmed) {
                        return;
                    }

                    if (employee && employee.pin) {
                        employee = await this.askPin(employee);
                    }
                    if (employee) {
                        this.env.pos.set_cashier(employee);
                    }
                    return employee;
                }
            }
        };

    Registries.Component.extend(LoginScreen, LoginScreencomissionist);

    return LoginScreen;
});
