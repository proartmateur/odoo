odoo.define('pw_pos_salesperson_emp.saleOrderButton', function (require) {
    'use strict';

    const SetSaleOrderButton = require('pos_sale.SaleOrderManagementControlPanel');
    const Registries = require('point_of_sale.Registries');
    const { isConnectionError } = require('point_of_sale.utils');
    const { Gui } = require('point_of_sale.Gui');

    const ResetSalesbutton = (SetSaleOrderButton) =>
        class extends SetSaleOrderButton {
            _computeDomain() {
                //let domain = [['state', '!=', 'cancel'],['invoice_status', '!=', 'invoiced'],['is_for_pos', '=', true],['pos_config_ids.id','=',this.env.pos.config.id]];
                let domain = [['state', 'in', ['draft','sale']],['invoice_status', 'in', ['to invoice','no']],['is_for_pos', '=', true],['pos_config_ids.id','=',this.env.pos.config.id],['x_studio_por_pagar','>',0]];
                const input = this.orderManagementContext.searchString.trim();
                if (!input) return domain;

                const searchConditions = this.orderManagementContext.searchString.split(/[,&]\s*/);
                if (searchConditions.length === 1) {
                    let cond = searchConditions[0].split(/:\s*/);
                    if (cond.length === 1) {
                      domain = domain.concat(Array(this.searchFields.length - 1).fill('|'));
                      domain = domain.concat(this.searchFields.map((field) => [field, 'ilike', `%${cond[0]}%`]));
                      return domain;
                    }
                }
                for (let cond of searchConditions) {
                    let [tag, value] = cond.split(/:\s*/);
                    if (!this.validSearchTags.has(tag)) continue;
                    domain.push([this.fieldMap[tag], 'ilike', `%${value}%`]);
                }
                return domain;
            }
        };

    Registries.Component.extend(SetSaleOrderButton, ResetSalesbutton);
    return ResetSalesbutton;
});
