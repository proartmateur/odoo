/** @odoo-module */

import { useBus, useService } from "@web/core/utils/hooks";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";
import { session } from "@web/session";

const { Component, useState, onWillStart, markup, xml } = owl;
var Dialog = require('web.Dialog');
const {qweb, _t} = require('web.core');
export class PedidosCurrency extends Component {
    get amount() {
        return parseFloat(this.props.amount).toFixed(2);
    }
}
PedidosCurrency.template = 'pedidos.PedidosCurrency';
PedidosCurrency.props = ["currency", "amount"];

export class PedidosOrderLine extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.state = useState({ mobileOpen: false });
    }

    get line() {
        return this.props.line;
    }

    get canEdit() {
        return !['sent', 'confirmed'].includes(this.line.raw_state);
    }

    get badgeClass() {
        const mapping = {'new': 'warning', 'confirmed': 'success', 'sent': 'info', 'ordered': 'danger'};
        return mapping[this.line.raw_state];
    }

    async updateQuantity(event) {
        const target = event.target;
        var qty = target.value;
        if(!qty){
            qty=0.0
        }
        await this.orm.call('product.order', 'update_quantity', [
            this.props.line.id,
            parseFloat(qty)
        ]);

        await this.props.onUpdateQuantity();
    }

    async updateNote(event){
        const target = event.target;
        var note = target.value;
        if(!note){
            note=''
        }
        await this.orm.call('product.order', 'update_note', [
            this.props.line.id,
            note
        ]);

        await this.props.onUpdateQuantity();
    }
}
PedidosOrderLine.template = 'pedidos.PedidosOrderLine';
PedidosOrderLine.props = ["line", "currency", "onUpdateQuantity", "openOrderLine"];
PedidosOrderLine.components = {
    PedidosCurrency,
};



export class PedidosEmployee extends Component {
    getDomain() {
        return [];
    }
}
PedidosEmployee.components = {
    Many2XAutocomplete,
}
PedidosEmployee.props = ["employename","onUpdateEmployee"];
PedidosEmployee.template = "pedidos.PedidosEmployee";

export class PedidosConfig extends Component {
    getDomain() {
        return [];
    }
}
PedidosConfig.components = {
    Many2XAutocomplete,
}
PedidosConfig.props = ["configname","onUpdateConfig"];
PedidosConfig.template = "pedidos.PedidosConfig";


export class PedidosUser extends Component {
    getDomain() {
        return [['id', '=', session.uid]];
    }
}
PedidosUser.components = {
    Many2XAutocomplete,
}
PedidosUser.props = ["username","isManager","onUpdateUser"];
PedidosUser.template = "pedidos.PedidosUser";


export class PedidosDashboard extends Component {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.user = useService("user");
        this.state = useState({
            infos: {},
            note:'',
            date:'',
        });

        useBus(this.env.bus, 'pedidos_update_dashboard', () => this._fetchLunchInfos());
        onWillStart(async () => {
            await this._fetchLunchInfos()
            //this.env.searchModel.updateLocationId(this.state.infos.user_location[0]);
        });
    }

    async pedidosRpc(route, args = {}) {
        return await this.rpc(route, {
            ...args,
            context: this.user.context,
            user_id: this.env.searchModel.pedidosState.userId,
            employee_id:this.env.searchModel.pedidosState.employeeId,
            config_id:this.env.searchModel.pedidosState.configId,
            note:this.env.searchModel.pedidosState.orderNote,
            expected_delivered_date:this.env.searchModel.pedidosState.expected_delivered_date,
        })
    }

    async _fetchLunchInfos() {
        this.state.infos = await this.pedidosRpc('/pedidos/infos');
    }

    async emptyCart() {
        await this.pedidosRpc('/pedidos/trash');
        await this._fetchLunchInfos();
    }

    get hasLines() {
        return this.state.infos.lines && this.state.infos.lines.length !== 0;
    }

    get canOrder() {
        return this.state.infos.raw_state === 'new';
    }

    get location() {
        return this.state.infos.user_location && this.state.infos.user_location[1];
    }

    async orderNow() {
        var self=this
        if (!this.canOrder) {
            return;
        }
        //await this.showPopup('ErrorPopup', { 'title', 'bodyyyy' });

        const save = await new Promise(resolve => {
            Dialog.confirm(this, _t("!Pedido Creado!"), {
                confirm_callback: () => resolve(true),
                cancel_callback: () => resolve(false),
            });
        });
        if (!save) {
            return;
        }else{
            await self.pedidosRpc('/pedidos/pay');
            await self._fetchLunchInfos();
            self.state.note=''
            self.state.date=''
        }

        
    }

    async onUpdateQuantity() {
        await this._fetchLunchInfos();
    }

    async onUpdateUser(value) {
        if (!value) {
            return;
        }
        this.env.searchModel.updateUserId(value[0].id);
        await this._fetchLunchInfos();
    }

    async onUpdateEmployee(value) {
        // if (!value) {
        //     return;
        // }
        this.env.searchModel.updateEmployeeId(!!value || value.length ? value[0].id : false);
        await this._fetchLunchInfos();
    }
    async onUpdateConfig(value) {
        // if (!value) {
        //     return;
        // }
        this.env.searchModel.updateconfigId(!!value || value.length ? value[0].id : false);
        await this._fetchLunchInfos();
    }
    async onUpdateOrderNote(value) {
        const target = event.target;
        var note = target.value;
        this.state.note=note
        if(!note){
            note=''
        }
        this.env.searchModel.updateOredeNote(note)
    }
    async onUpdateExpectedDate(value) {
        const target = event.target;
        var date = target.value;
        this.state.date=date
        if(!date){
            date=''
        }
        this.env.searchModel.updateExpectedDeliveredDate(date)
    }
    
}
PedidosDashboard.components = {
    PedidosCurrency,
    PedidosOrderLine,
    PedidosUser,
    PedidosEmployee,
    PedidosConfig,
    Many2XAutocomplete,
};
PedidosDashboard.props = ["openOrderLine"];
PedidosDashboard.template = 'pedidos.PedidosDashboard';
