odoo.define('point_of_sale.IntInputPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    const { onMounted, useRef, useState } = owl;

    // formerly IntInputPopupWidget
    class IntInputPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = useState({
                inputValue: this.props.startingValue,
                inputError: null,
                showError: false,
            });
            this.inputRef = useRef('input');
            onMounted(this.onMounted);
        }
        onMounted() {
            this.inputRef.el.focus();
        }
        getPayload() {

            return this.state.inputValue;
        }
        _onPressEnterKey(event){
            var self=this
            if(event.code == 'Enter'){
                self.confirm()
            }
        }

        getProductUnit() {
            const {uom_id} = this.props.data
            console.log("getProductUnit:")
            console.log(uom_id)
            if(uom_id) {
                return uom_id[1]
            }
            return 'no-unit'
        }

        isInKg() {
            const unit = this.getProductUnit()
            console.log("isInKg:")
            console.log(unit)
            return unit.toLowerCase() === 'kg'
        }

        canSellThisQuantity(quantity) {
            const isInteger = (quantity % 1) === 0
            if(!isInteger){
                if(this.isInKg()) {
                    return true
                }
                this.state.inputError = 'No puede comprar o vender esta cantidad de producto'
                return false
            }

            if(quantity === 0) {

                this.state.inputError = 'Ingrese una cantidad mayor que 0'
                return false
            }
            return true
        }

        async confirm() {
            console.log('CONFIRM */*/*/')
            const val = Number(this.state.inputValue)
            console.log(this.props.data)
            if(this.canSellThisQuantity(val)) {
                this.env.posbus.trigger('close-popup', {
                    popupId: this.props.id,
                    response: { confirmed: true, payload: await this.getPayload() },
                });
            } else {
                this.state.showError = true
            }
        }

        validateQuantity(){
            const val = Number(this.state.inputValue)
            if(!this.canSellThisQuantity(val))
            {
                this.state.showError = true
            } else {
                this.state.inputError = null
                this.state.showError = false
            }

        }
    }
    IntInputPopup.template = 'IntInputPopup';
    IntInputPopup.defaultProps = {
        confirmText: _lt('Ok'),
        cancelText: _lt('Cancel'),
        title: '',
        body: '',
        startingValue: '',
        placeholder: '',
        data: {}
    };

    Registries.Component.add(IntInputPopup);

    return IntInputPopup;
});
