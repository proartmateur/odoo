odoo.define('pw_pos_salesperson_emp.get_order_screen', function (require) {
    const SaleOrderManagementScreen = require('pos_sale.SaleOrderManagementScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    const { sprintf } = require('web.utils');
    const { parse } = require('web.field_utils');
    const { Orderline } = require('point_of_sale.models');
    const SaleOrderFetcher = require('pos_sale.SaleOrderFetcher');

    const pediosSaleOrdescreeninherite = (SaleOrderManagementScreen) =>
        class extends SaleOrderManagementScreen {
            setup() {
                super.setup();
                this.pedido_fisrt=1
                /*useListener('click-order', this._onShowDetails)
                this.mobileState = useState({ showDetails: false });*/
            }
            get orders() {
                if(this.pedido_fisrt <= 4){
                    this.pedido_fisrt+=1
                    return []
                }else{
                    //this.pedido_fisrt=false
                    return SaleOrderFetcher.get();
                }
                
            }

        };

    Registries.Component.extend(SaleOrderManagementScreen, pediosSaleOrdescreeninherite);

    return SaleOrderManagementScreen;
});
