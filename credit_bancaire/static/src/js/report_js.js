/** @odoo-module **/

import { Component, onMounted, useState } from "@odoo/owl";
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category('actions');

class EmployeeDashboard extends Component {
    setup() {
        super.setup();

        this.orm = useService("orm");
        this.employeeDashboard = useState({ data: [] , header : [], pay_customer: [], data_supplier: [], pay_supplier:[], total: []});
        onMounted(() => {
            document.getElementById('fetch-data-btn').addEventListener('click', this.loadData.bind(this));
        });
    }

    async loadData() {
        try {
            const data = await this.orm.call(
                'account.payment','get_time_off',[],
            );
            console.log(1);
            var payCustomerRow = data.filter(function(row) {
                return row[0] === 'Paiement clients';
            });
            var invCustomerRow = data.filter(function(row) {
                return !['Paiement clients'].includes(row[0]);
            });
            console.log(payCustomerRow);
            this.employeeDashboard.pay_customer = payCustomerRow;
            this.employeeDashboard.data = invCustomerRow;

            const supplier_data = await this.orm.call(
                'account.payment','get_supplier_off',[],
            );

            console.log(2);
            var paySupplierRow = supplier_data.filter(function(row) {
                return row[0] === 'Paiement fournisseurs';
            });
            var invSupplierRow = supplier_data.filter(function(row) {
                return !['Paiement fournisseurs'].includes(row[0]);
            });
            console.log(paySupplierRow);
            this.employeeDashboard.pay_supplier = paySupplierRow;
            this.employeeDashboard.data_supplier = invSupplierRow;
            const total = await this.orm.call(
                'account.payment','get_total',[],
            );

            console.log(3);
            this.employeeDashboard.total = total;
            console.log(total);
            const header = await this.orm.call(
                'account.payment','get_header',[],
            );
            console.log(4);
            this.employeeDashboard.header = header;
        } catch (error) {
            console.error('Failed to fetch data:', error);
        }
    }
}

EmployeeDashboard.template = 'EmployeeDashboard';
actionRegistry.add('tag_test', EmployeeDashboard);
