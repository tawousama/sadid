/** @odoo-module **/

import { Component, onMounted, useState } from "@odoo/owl";
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category('actions');

class CashflowDashboard extends Component {
    setup() {
        super.setup();
        this.state = useState({
            bankSelection: '',  // Initial value
            banks: [],
            endDate: '',
        });
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.cashflowDashboard = useState({ data: [] , header : [], headerGreen: [], headerRed: []});
        onMounted(() => {
            this.fetchBanks();
            document.getElementById('fetch-data-btn').addEventListener('click', this.loadData.bind(this));
        });
    }

    async fetchBanks() {
        const response = await this.rpc('/get_banques');
        this.state.banks = response;
        if (this.state.banks.length > 0) {
            this.state.bankSelection = this.state.banks[0].id;
        }
    }

    async loadData() {
        try {
            const header = await this.orm.call(
                'cashflow.report','get_header',[ this.state.endDate, this.state.bankSelection],
            );
            const headerRed = await this.orm.call(
                'cashflow.report','index_header_red',[this.state.endDate, this.state.bankSelection]
            );
            this.cashflowDashboard.headerRed = headerRed;
            console.log(headerRed);
            const headerGreen = await this.orm.call(
                'cashflow.report','index_header_green',[this.state.endDate, this.state.bankSelection]
            );
            this.cashflowDashboard.headerGreen = headerGreen;
            this.cashflowDashboard.header = header;
            const data = await this.orm.call(
                'cashflow.report','get_values',[ this.state.endDate, this.state.bankSelection],
            );
            this.cashflowDashboard.data = data;
        } catch (error) {
            console.error('Failed to fetch data:', error);
        }
    }
}

CashflowDashboard.template = 'CashflowDashboard';
actionRegistry.add('cashflow_dashboard', CashflowDashboard);
