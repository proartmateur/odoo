odoo.define('pw_pos_restrict_refund.RefundButton', function (require) {
    'use strict';

    const RefundButton = require('point_of_sale.RefundButton');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');

    const { _t } = require('web.core');

    const PWRestrictRefundButton = (RefundButton) =>
        class extends RefundButton {
            async _onClick() {
                if(this.env.pos.config.pw_allow_refund) {
                    const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                        isPassword: true,
                        title: this.env._t('Password ?'),
                        startingValue: null,
                    });
                    if (!confirmed) return;
                    if (inputPin == this.env.pos.config.pw_refund_password) {
                        super._onClick()
                    } else {
                        await this.showPopup('ErrorPopup', {
                            title: this.env._t('Incorrect Password'),
                        });
                        return;
                    }
                }
                else {
                    super._onClick()
                }
            }
        };

    Registries.Component.extend(RefundButton, PWRestrictRefundButton);

    return RefundButton;
});
