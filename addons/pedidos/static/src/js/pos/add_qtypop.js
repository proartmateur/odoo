/** @odoo-module **/

import ProductScreen from 'point_of_sale.ProductScreen';
import Registries from 'point_of_sale.Registries';
import { useBarcodeReader } from 'point_of_sale.custom_hooks';
import NumberBuffer from 'point_of_sale.NumberBuffer';

export const QtyProductScreen = (ProductScreen) =>
    class extends ProductScreen {
        async _clickProduct(event) {
            var self=this
            const { confirmed, payload: qty } = await this.showPopup('IntInputPopup', {
                title: this.env._t(`Establecer cantidad :`),
                startingValue: '',
                data: event.detail
            });
            if(confirmed){
                //this.props.line.set_multiple_qty(parseFloat(qty) || 0);
                if (!self.currentOrder) {
                self.env.pos.add_new_order();
                }
                const product = event.detail;
                const options = await self._getAddProductOptions(product);
                // Do not add product if options is undefined.
                if (!options) return;
                // Add the product after having the extra information.
                options.quantity=qty
                await self._addProduct(product, options);
                NumberBuffer.reset();
            }

        }
    };

Registries.Component.extend(ProductScreen, QtyProductScreen);
