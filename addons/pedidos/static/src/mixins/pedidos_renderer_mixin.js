/** @odoo-module */

import { useBus, useService } from "@web/core/utils/hooks";
import { _t } from "web.core";
//import { ConfirmationDialog } from "@pedidos/core/confirmation_dialog/ConfirmationDialog2";

import { Dialog } from "@web/core/dialog/dialog";
import { _lt } from "@web/core/l10n/translation";
import { useChildRef } from "@web/core/utils/hooks";

const { Component , onMounted} = owl;

export class ConfirmationDialog2 extends Component {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.env.dialogData.close = () => this._cancel();
        this.modalRef = useChildRef();
        this.isConfirmedOrCancelled = false; // ensures we do not confirm and/or cancel twice
        
        onMounted(() => {
            if(this.modalRef.el){
                $(this.modalRef.el.querySelector(".qty")).focus();
            }
        });
    }
    
    async _cancel() {
        if (this.isConfirmedOrCancelled) {
            return;
        }
        this.isConfirmedOrCancelled = true;
        this.disableButtons();
        if (this.props.cancel) {
            try {
                await this.props.cancel();
            } catch (e) {
                this.props.close();
                throw e;
            }
        }
        this.props.close();
    }
    async _confirm() {
        var self=this
        if(!self.qty){
            alert("Please Add Qty")
            return
        }
        if(!self.note){
            self.note=''
        }
        this.rpc('/add/product/pedidios', {
                context: self.props.context,
                productId: self.props.productId,
                Qty:self.qty,
                Note:self.note,
            }).then(function(e){
                self.env.bus.trigger('pedidos_update_dashboard')
                self.props.close()
            })
        //this.props.close();
    }
    disableButtons() {
        if (!this.modalRef.el) {
            return; // safety belt for stable versions
        }
        for (const button of [...this.modalRef.el.querySelectorAll(".modal-footer button")]) {
            button.disabled = true;
        }
    }
    onKeyDownQty(ev) {
        if (ev.target.value) {
            this.qty = ev.target.value;
        }
    }
    onKeyDownNote(ev){
        if (ev.target.value) {
            this.note = ev.target.value;
        }
    }
}
ConfirmationDialog2.template = "pedidos.ConfirmationDialog2";
ConfirmationDialog2.components = { Dialog };
ConfirmationDialog2.props = {
    close: Function,
    title: {
        validate: (m) => {
            return (
                typeof m === "string" || (typeof m === "object" && typeof m.toString === "function")
            );
        },
        optional: true,
    },
    body: String,
    uom:String,
    context:Object,
    productId:Number,
    confirm: { type: Function, optional: true },
    confirmLabel: { type: String, optional: true },
    cancel: { type: Function, optional: true },
    cancelLabel: { type: String, optional: true },
};
ConfirmationDialog2.defaultProps = {
    confirmLabel: _lt("Add to List"),
    cancelLabel: _lt("Cancel"),
    title: _lt("Add Product"),
};

export const PedidosRendererMixin = {
    setup() {
        this._super(...arguments);
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.dialogService = useService("dialog");
        useBus(this.env.bus, 'pedidos_open_order', (ev) => this.openOrderLine(ev.detail.productId,ev.detail.productName,ev.detail.productUom));
    },

    openOrderLine(productId, productName,productUom) {
        if(this.env.searchModel.pedidosState.employeeId){
            let context = {};
            var self=this
            if (this.env.searchModel.pedidosState.employeeId) {
                context['default_empoyee_id'] = this.env.searchModel.pedidosState.employeeId;
            }
            if (this.env.searchModel.pedidosState.userId) {
                context['default_user_id'] = this.env.searchModel.pedidosState.userId;
            }
            if (this.env.searchModel.pedidosState.configId) {
                context['default_config_id'] = this.env.searchModel.pedidosState.configId;
            }

            const dialogProps = {
                body: this.env._t(
                    "You Selected '"+productName+"'"
                ),
                uom:productUom,
                context:context,
                productId:productId,
                confirm: () => this.model.root.archive(),
                cancel: () => {},
            };
            this.dialogService.add(ConfirmationDialog2, dialogProps);
            /*this.rpc('/add/product/pedidios', {
                context: context,
                productId: productId,
            }).then(function(e){
                self.env.bus.trigger('pedidos_update_dashboard')
            })*/
            //self.env.bus.trigger('pedidos_update_dashboard')
        }
        else{
            alert("Please Select Cliente!")
        }
        
    },
}



