odoo.define('pedidos.pediosSaleOrderManagementScreenn', function (require) {
    const SaleOrderManagementScreen = require('pos_sale.SaleOrderManagementScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    const { sprintf } = require('web.utils');
    const { parse } = require('web.field_utils');
    const { Orderline } = require('point_of_sale.models');

    const pediosSaleOrderManagementScreen = (SaleOrderManagementScreen) =>
        class extends SaleOrderManagementScreen {
            async _onClickSaleOrder(event) {
                const clickedOrder = event.detail;
                const { confirmed, payload: selectedOption } = await this.showPopup('SelectionPopup',
                    {
                        title: this.env._t('What do you want to do?'),
                        list: [{id:"0", label: this.env._t("Apply a down payment"), item: false}],
                    });

                if(confirmed){
                  let currentPOSOrder = this.env.pos.get_order();
                  let sale_order = await this._getSaleOrder(clickedOrder.id);
                  try {
                    await this.env.pos.load_new_partners();
                  }
                  catch (_error){
                  }
                  let order_partner = this.env.pos.db.get_partner_by_id(sale_order.partner_id[0])
                  if(order_partner){
                    currentPOSOrder.set_partner(order_partner);
                  } else {
                    try {
                        await this.env.pos._loadPartners([sale_order.partner_id[0]]);
                    }
                    catch (_error){
                        const title = this.env._t('Customer loading error');
                        const body = _.str.sprintf(this.env._t('There was a problem in loading the %s customer.'), sale_order.partner_id[1]);
                        await this.showPopup('ErrorPopup', { title, body });
                    }
                    currentPOSOrder.set_partner(this.env.pos.db.get_partner_by_id(sale_order.partner_id[0]));
                  }
                  let orderFiscalPos = sale_order.fiscal_position_id ? this.env.pos.fiscal_positions.find(
                      (position) => position.id === sale_order.fiscal_position_id[0]
                  )
                  : false;
                  if (orderFiscalPos){
                      currentPOSOrder.fiscal_position = orderFiscalPos;
                  }
                  let orderPricelist = sale_order.pricelist_id ? this.env.pos.pricelists.find(
                      (pricelist) => pricelist.id === sale_order.pricelist_id[0]
                  )
                  : false;
                  if (orderPricelist){
                      currentPOSOrder.set_pricelist(orderPricelist);
                  }

                  if (selectedOption){
                    // settle the order
                    let lines = sale_order.order_line;
                    let product_to_add_in_pos = lines.filter(line => !this.env.pos.db.get_product_by_id(line.product_id[0])).map(line => line.product_id[0]);
                    if (product_to_add_in_pos.length){
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('Products not available in POS'),
                            body:
                                this.env._t(
                                    'Some of the products in your Sale Order are not available in POS, do you want to import them?'
                                ),
                            confirmText: this.env._t('Yes'),
                            cancelText: this.env._t('No'),
                        });
                        if (confirmed){
                            await this.env.pos._addProducts(product_to_add_in_pos);
                        }

                    }

                    /**
                     * This variable will have 3 values, `undefined | false | true`.
                     * Initially, it is `undefined`. When looping thru each sale.order.line,
                     * when a line comes with lots (`.lot_names`), we use these lot names
                     * as the pack lot of the generated pos.order.line. We ask the user
                     * if he wants to use the lots that come with the sale.order.lines to
                     * be used on the corresponding pos.order.line only once. So, once the
                     * `useLoadedLots` becomes true, it will be true for the succeeding lines,
                     * and vice versa.
                     */
                    let useLoadedLots;

                    for (var i = 0; i < lines.length; i++) {
                        let line = lines[i];
                        if (!this.env.pos.db.get_product_by_id(line.product_id[0])){
                            continue;
                        }

                        let new_line = Orderline.create({}, {
                            pos: this.env.pos,
                            order: this.env.pos.get_order(),
                            product: this.env.pos.db.get_product_by_id(line.product_id[0]),
                            description: line.name,
                            price: line.price_unit,
                            tax_ids: orderFiscalPos ? undefined : line.tax_id,
                            price_manually_set: true,
                            sale_order_origin_id: clickedOrder,
                            sale_order_line_id: line,
                            customer_note: line.customer_note,
                        });

                        if (
                            new_line.get_product().tracking !== 'none' &&
                            (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots) &&
                            line.lot_names.length > 0
                        ) {
                            // Ask once when `useLoadedLots` is undefined, then reuse it's value on the succeeding lines.
                            const { confirmed } =
                                useLoadedLots === undefined
                                    ? await this.showPopup('ConfirmPopup', {
                                          title: this.env._t('SN/Lots Loading'),
                                          body: this.env._t(
                                              'Do you want to load the SN/Lots linked to the Sales Order?'
                                          ),
                                          confirmText: this.env._t('Yes'),
                                          cancelText: this.env._t('No'),
                                      })
                                    : { confirmed: useLoadedLots };
                            useLoadedLots = confirmed;
                            if (useLoadedLots) {
                                new_line.setPackLotLines({
                                    modifiedPackLotLines: [],
                                    newPackLotLines: (line.lot_names || []).map((name) => ({ lot_name: name })),
                                });
                            }
                        }
                        new_line.setQuantityFromSOL(line);
                        new_line.set_unit_price(line.price_unit);
                        new_line.set_discount(line.discount);
                        this.env.pos.get_order().add_orderline(new_line);
                    }
                  }
                  else {
                    // apply a downpayment
                    if (this.env.pos.config.down_payment_product_id){

                        let lines = sale_order.order_line;
                        let tab = [];

                        for (let i=0; i<lines.length; i++) {
                            tab[i] = {
                                'product_name': lines[i].product_id[1],
                                'product_uom_qty': lines[i].product_uom_qty,
                                'price_unit': lines[i].price_unit,
                                'total': lines[i].price_total,
                            };
                        }
                        let down_payment_product = this.env.pos.db.get_product_by_id(this.env.pos.config.down_payment_product_id[0])
                        let down_payment_tax = this.env.pos.taxes_by_id[down_payment_product.taxes_id] || false ;
                        let down_payment;
                        if (down_payment_tax) {
                            down_payment = down_payment_tax.price_include ? sale_order.amount_total : sale_order.amount_untaxed;
                        }
                        else{
                            down_payment = sale_order.amount_total;
                        }
                        //payload=this.env.pos.format_currency(sale_order.amount_total)
                        //Percentage of
                        const { confirmed, payload } = await this.showPopup('NumberPopup', {
                            title: sprintf(this.env._t("Aplicar un pago %s"), this.env.pos.format_currency(sale_order.amount_total)),
                            startingValue: sale_order.amount_total,
                            isInputSelected: true,
                        });
                        if (confirmed){
                            down_payment = payload;
                        }


                        let new_line = Orderline.create({}, {
                            pos: this.env.pos,
                            order: this.env.pos.get_order(),
                            product: down_payment_product,
                            price: down_payment,
                            price_manually_set: true,
                            sale_order_origin_id: clickedOrder,
                            down_payment_details: tab,
                        });
                        new_line.set_unit_price(down_payment);
                        this.env.pos.get_order().add_orderline(new_line);
                    }
                    else {
                        const title = this.env._t('No down payment product');
                        const body = this.env._t(
                            "It seems that you didn't configure a down payment product in your point of sale.\
                            You can go to your point of sale configuration to choose one."
                        );
                        await this.showPopup('ErrorPopup', { title, body });
                    }
                  }

                  this.close();
                }

        }
            /*credit_error_action() {
                this.showPopup('ErrorPopup', {
                    body: this.env._t('Go to payment screen to use cards'),
                });
            }*/
        };

    Registries.Component.extend(SaleOrderManagementScreen, pediosSaleOrderManagementScreen);

    return SaleOrderManagementScreen;
});
