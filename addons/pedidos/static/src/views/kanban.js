/** @odoo-module */

import { patch } from '@web/core/utils/patch';
import { registry } from '@web/core/registry';

import { kanbanView } from '@web/views/kanban/kanban_view';
import { KanbanRecord } from '@web/views/kanban/kanban_record';
import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';

import { PedidosDashboard } from '../components/pedidos_dashboard';
import { PedidosRendererMixin } from '../mixins/pedidos_renderer_mixin';

import { PedidosSearchModel } from './search_model';
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { useBus, useService } from "@web/core/utils/hooks";
import { useSetupView } from "@web/views/view_hook";
import { usePager } from "@web/search/pager_hook";

import { useModel } from "@web/views/model";
import { useViewButtons } from "@web/views/view_button/view_button_hook";

import { Component, useRef } from "@odoo/owl";
export class PedidosKanbanRecord extends KanbanRecord {
    onGlobalClick(ev) {
        this.env.bus.trigger('pedidos_open_order', {productId: this.props.record.resId,productName:this.props.record.data.name,productUom:this.props.record.data.uom_id[1]});
    }
}

export class PedidosKanbanRenderer extends KanbanRenderer {
    getGroupsOrRecords() {
        if (!this.env.searchModel.pedidosState.employeeId) return [];
        return super.getGroupsOrRecords();
    }
}

export class PedidosKanbanController extends KanbanController {
     setup() {
        this.actionService = useService("action");
        const { Model, resModel, fields, archInfo, limit, defaultGroupBy, state } = this.props;
        const { rootState } = state || {};
        this.model = useModel(Model, {
            activeFields: archInfo.activeFields,
            progressAttributes: archInfo.progressAttributes,
            fields,
            resModel,
            handleField: archInfo.handleField,
            limit: archInfo.limit || limit,
            onCreate: archInfo.onCreate,
            quickCreateView: archInfo.quickCreateView,
            defaultGroupBy,
            defaultOrder: archInfo.defaultOrder,
            viewMode: "kanban",
            openGroupsByDefault: true,
            tooltipInfo: archInfo.tooltipInfo,
            rootState,
        });

        const rootRef = useRef("root");
        useViewButtons(this.model, rootRef, {
            beforeExecuteAction: this.beforeExecuteActionButton.bind(this),
            afterExecuteAction: this.afterExecuteActionButton.bind(this),
        });
        useSetupView({
            rootRef,
            getGlobalState: () => {
                return {
                    resIds: this.model.root.records.map((rec) => rec.resId), // WOWL: ask LPE why?
                };
            },
            getLocalState: () => {
                return {
                    rootState: this.model.root.exportState(),
                };
            },
        });
        usePager(() => {
            const root = this.model.root;
            const { count, hasLimitedCount, isGrouped, limit, offset } = root;
            var new_count=count
            if(count > 200){
                new_count=200
            }
            /*else:
                new_count=*/
            //count=20
            if (!isGrouped) {
                return {
                    offset: offset,
                    limit: limit,
                    total: new_count,
                    onUpdate: async ({ offset, limit }) => {
                        this.model.root.offset = offset;
                        this.model.root.limit = limit;
                        await this.model.root.load();
                        await this.onUpdatedPager();
                        this.render(true); // FIXME WOWL reactivity
                    },
                    updateTotal: hasLimitedCount ? () => root.fetchCount() : undefined,
                };
            }
        });
    }

   
}

patch(PedidosKanbanRenderer.prototype, 'pedidos_kanban_renderer_mixin', PedidosRendererMixin);

PedidosKanbanRenderer.template = 'pedidos.KanbanRenderer';
PedidosKanbanRenderer.components = {
    ...PedidosKanbanRenderer.components,
    PedidosDashboard,
    KanbanRecord: PedidosKanbanRecord,
}

registry.category('views').add('pedidos_kanban', {
    ...kanbanView,
    Controller: PedidosKanbanController,
    Renderer: PedidosKanbanRenderer,
    SearchModel: PedidosSearchModel,
});
