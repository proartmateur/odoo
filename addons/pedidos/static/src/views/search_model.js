/** @odoo-module */

import { useService } from "@web/core/utils/hooks";

import { Domain } from '@web/core/domain';
import { SearchModel } from '@web/search/search_model';

const { useState, onWillStart } = owl;


export class PedidosSearchModel extends SearchModel {
    setup() {
        super.setup(...arguments);

        this.rpc = useService('rpc');
        this.pedidosState = useState({
            userId: false,
            employeeId:false,
            configId:false,
            orderNote:'',
            expected_delivered_date:''
        });
    }

    exportState() {
        const state = super.exportState();
        state.userId = this.pedidosState.userId;
        state.employeeId = this.pedidosState.employeeId;
        state.configId=this.pedidosState.configId;
        return state;
    }

    _importState(state) {
        super._importState(...arguments);
        
        if (state.userId) {
            this.pedidosState.userId = state.userId;
        }
        if (state.employeeId) {
            this.pedidosState.employeeId = state.employeeId;
        }
        if (state.configId) {
            this.pedidosState.configId = state.configId;
        }
        if (state.orderNote) {
            this.pedidosState.orderNote = state.orderNote;
        }
        if (state.expected_delivered_date) {
            this.pedidosState.expected_delivered_date = state.expected_delivered_date;
        }
    }

    updateUserId(userId) {
        this.pedidosState.userId = userId;
        this._notify();
    }
    updateEmployeeId(employeeId) {
        this.pedidosState.employeeId = employeeId;
        this._notify();
    }
    updateconfigId(configId) {
        this.pedidosState.configId = configId;
        this._notify();
    }
    updateOredeNote(orderNote) {
        this.pedidosState.orderNote = orderNote;
        this._notify();
    }
    updateExpectedDeliveredDate(date) {
        this.pedidosState.expected_delivered_date = date;
        this._notify();
    }
    _getDomain(params = {}) {
        const domain = super._getDomain(params);
        return Domain.and([
            domain
        ]).toList();
    }
}
