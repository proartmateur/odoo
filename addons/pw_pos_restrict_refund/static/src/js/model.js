odoo.define('pw_pos_restrict_refund.model', function (require) {
    "use strict";

var { PosGlobalState, Order } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');


const PosHrPosGlobalStatepedios = (PosGlobalState) => class PosHrPosGlobalStatepedios extends PosGlobalState {
    async _processData(loadedData) {
        await super._processData(...arguments);
        if (this.config.module_pos_hr) {
            this.comissionists = loadedData['comissionists'];
            // this.reset_cashier();
        }
    }
    
}
Registries.Model.extend(PosGlobalState, PosHrPosGlobalStatepedios);



});
