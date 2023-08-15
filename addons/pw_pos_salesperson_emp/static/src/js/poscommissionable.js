/** @odoo-module **/

import ProductScreen from 'point_of_sale.ProductScreen';
import Registries from 'point_of_sale.Registries';
//import { useBarcodeReader } from 'point_of_sale.custom_hooks';

export const PosCommissionable = (ProductScreen) =>
    class extends ProductScreen {
        async _onClickPay() {
            const order = this.env.pos.get_order();
            var self=this
            //const Orderline = order.get_orderlines()
            if (order) {
                var is_all_user_set=true
                order.get_orderlines().forEach(function (orderline) {
                    var product = orderline.product;
                    if(product.is_commissionable){
                        if(!orderline.user_id){
                            is_all_user_set=false
                            
                        }
                    }
                   
                });
                if(is_all_user_set){
                    return super._onClickPay(...arguments);
                }else{
                    self.showPopup('ErrorPopup', {
                            title: self.env._t('Please Set All Salesperson.'),
                        });
                }
            }else{
                return super._onClickPay(...arguments);
            }
            
        }
        
    };

Registries.Component.extend(ProductScreen, PosCommissionable);
