from odoo import http
from odoo.http import request
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class CreditBanqueController(http.Controller):

    @http.route('/get_banques', type='json', auth='user')
    def get_banques(self):
        banques = request.env['credit.banque'].search([('has_autorisation', '=', True)])
        return [{'id': banque.id, 'name': banque.name} for banque in banques]


class CashflowReport(models.AbstractModel):
    _name = 'cashflow.report'

    @api.model
    def get_header(self, dateEnd, bank=1):
        dateStart = fields.Date.today()
        print(dateEnd)
        if dateEnd == '':
            dateEnd = fields.Date.today() + timedelta(days=30)
        domain = [('state', '=', 'draft')]
        if dateStart:
            domain.append(('date_prevue_deblocage', '!=', False))
            domain.append(('date_prevue_deblocage', '>=', dateStart))
        else:
            domain.append(('date_prevue_deblocage', '!=', False))
        if dateEnd:
            domain.append(('date_prevue_deblocage', '!=', False))
            domain.append(('date_prevue_deblocage', '<=', dateEnd))
        else:
            domain.append(('date_prevue_deblocage', '!=', False))
        if bank:
            domain.append(('banque_id', '=', int(bank)))
        data = self.env['credit.operation.deb'].search(domain)
        headers = ['Date']
        for d in data:
            if d.type != False:
                if 'Deb. ' + d.type.name not in headers:
                    headers.append('Deb. ' + d.type.name)
            elif d.type_ids[0] != False:
                if 'Deb. ' + d.type_ids[0].name not in headers:
                    headers.append('Deb. ' + d.type.name)
        headers.append('Chèque clients en circulation')
        domain = [('state', '=', 'not_paid')]
        if dateStart:
            domain.append(('echeance_date', '>=', dateStart))
        else:
            domain.append(('echeance_date', '!=', False))
        if dateEnd:
            domain.append(('echeance_date', '<=', dateEnd))
        else:
            domain.append(('echeance_date', '!=', False))
        if bank:
            domain.append(('banque', '=', int(bank)))
        data = self.env['credit.echeance'].search(domain)
        for d in data:
            if 'Ech. ' + d.type.name not in headers:
                headers.append('Ech. ' + d.type.name)
        headers.append('Chèques fournisseurs en circulation')
        headers.append('Salaire en circulation')
        headers.append('G50 en circulation')
        headers.append('Solde Banque')
        headers_dict = []
        for index,item in enumerate(headers):
            element = {
                'key': 'header_' + str(index),
                'value': item
            }
            headers_dict.append(element)
        return headers_dict

    @api.model
    def get_values(self, dateEnd, bank=1):
        dateStart = fields.Date.today()
        print(dateEnd)
        if dateEnd != '':
            dateEnd = fields.Date.today() + timedelta(days=30)
        headers_items = self.get_header(dateEnd, bank)
        headers = []
        for item in headers_items:
            headers.append(item['value'])
        domain = [('state', '=', 'draft')]
        if dateStart:
            domain.append(('date_prevue_deblocage', '>=', dateStart))
        else:
            domain.append(('date_prevue_deblocage', '!=', False))
        if dateEnd:
            domain.append(('date_prevue_deblocage', '<=', dateEnd))
        else:
            domain.append(('date_prevue_deblocage', '!=', False))
        if bank:
            domain.append(('banque_id', '=', int(bank)))
        data = self.env['credit.operation.deb'].search(domain)
        final_list = []
        for d in data:
            type_added = False
            date = d.date_prevue_deblocage.strftime('%Y-%m-%d')
            if len(final_list) != 0:
                for line in final_list:
                    if line[0] == date:
                        index_bank = headers.index('Deb. ' + d.type.name)
                        index_line = final_list.index(line)
                        line[index_bank] = round(d.montant_debloque, 2) + line[index_bank]
                        final_list[index_line] = line
                        type_added = True
                        break
            if not type_added:
                sub_line = []
                sub_line.append(date)
                for i in range(len(headers) - 1):
                    sub_line.append(0)
                if 'Deb. ' + d.type.name in headers:
                    index = headers.index('Deb. ' + d.type.name)
                    sub_line[index] = round(d.montant_debloque, 2)
                final_list.append(sub_line)
        print(1)
        domain = [('state', '=', 'not_paid')]
        if dateStart:
            domain.append(('echeance_date', '>=', dateStart))
        else:
            domain.append(('echeance_date', '!=', False))
        if dateEnd:
            domain.append(('echeance_date', '<=', dateEnd))
        else:
            domain.append(('echeance_date', '!=', False))
        if bank:
            domain.append(('banque', '=', int(bank)))
        data = self.env['credit.echeance'].search(domain)
        for d in data:
            type_added = False
            date = d.echeance_date.strftime('%Y-%m-%d')
            if len(final_list) != 0:
                for line in final_list:
                    if line[0] == date:
                        index_bank = headers.index('Ech. ' +d.type.name)
                        index_line = final_list.index(line)
                        line[index_bank] = round(d.montant_a_rembourser, 2) + line[index_bank]
                        final_list[index_line] = line
                        type_added = True
                        break
            if not type_added:
                sub_line = []
                sub_line.append(date)
                for i in range(len(headers) - 1):
                    sub_line.append(0)
                if 'Ech. ' + d.type.name in headers:
                    index = headers.index('Ech. ' + d.type.name)
                    sub_line[index] = round(d.montant_a_rembourser, 2)
                final_list.append(sub_line)
        print(2)
        index_client = headers.index('Chèque clients en circulation')
        domain = [('state', '=', 'draft'), ('partner_type', '=', 'customer')]
        if dateStart:
            domain.append(('date_encaissement_dec', '>=', dateStart))
        else:
            domain.append(('date_encaissement_dec', '!=', False))
        if dateEnd:
            domain.append(('date_encaissement_dec', '<=', dateEnd))
        else:
            domain.append(('date_encaissement_dec', '!=', False))
        if bank:
            journal_bank = self.env['credit.banque'].search([('id', '=', int(bank))])
            if journal_bank.journal_id:
                domain.append(('journal_id', '=', journal_bank.journal_id.id))
        data_client = self.env['account.payment'].search(domain)
        for d in data_client:
            type_added = False
            date = d.date_encaissement_dec.strftime('%Y-%m-%d')
            if len(final_list) != 0:
                for line in final_list:
                    if line[0] == date:
                        index_bank = index_client
                        index_line = final_list.index(line)
                        line[index_bank] = round(d.amount, 2) + line[index_bank]
                        final_list[index_line] = line
                        type_added = True
                        break
            if not type_added:
                sub_line = []
                sub_line.append(date)
                for i in range(len(headers) - 1):
                    sub_line.append(0)
                index = index_client
                sub_line[index] = round(d.amount, 2)
                final_list.append(sub_line)
        print(3)
        index_fourn = headers.index('Chèques fournisseurs en circulation')
        domain = [('state', '=', 'draft'), ('partner_type', '=', 'supplier'), ('autre_type', '=', False)]
        if dateStart:
            domain.append(('date_encaissement_dec', '>=', dateStart))
        else:
            domain.append(('date_encaissement_dec', '!=', False))
        if dateEnd:
            domain.append(('date_encaissement_dec', '<=', dateEnd))
        else:
            domain.append(('date_encaissement_dec', '!=', False))
        if bank:
            journal_bank = self.env['credit.banque'].search([('id', '=', int(bank))])
            if journal_bank.journal_id:
                domain.append(('journal_id', '=', journal_bank.journal_id.id))
        data_fourn = self.env['account.payment'].search(domain)
        for d in data_fourn:
            type_added = False
            date = d.date_encaissement_dec.strftime('%Y-%m-%d')
            if len(final_list) != 0:
                for line in final_list:
                    if line[0] == date:
                        index_bank = index_fourn
                        index_line = final_list.index(line)
                        line[index_bank] = round(d.amount, 2) + line[index_bank]
                        final_list[index_line] = line
                        type_added = True
                        break
            if not type_added:
                sub_line = []
                sub_line.append(date)
                for i in range(len(headers) - 1):
                    sub_line.append(0)
                index = index_fourn
                sub_line[index] = round(d.amount, 2)
                final_list.append(sub_line)
        print(4)
        index_fourn = headers.index('Salaire en circulation')
        domain = [('state', '=', 'draft'), ('partner_type', '=', 'supplier'), ('autre_type', '=', 'salaire')]
        if dateStart:
            domain.append(('date', '>=', dateStart))
        else:
            domain.append(('date', '!=', False))
        if dateEnd:
            domain.append(('date', '<=', dateEnd))
        else:
            domain.append(('date', '!=', False))
        if bank:
            journal_bank = self.env['credit.banque'].search([('id', '=', int(bank))])
            if journal_bank.journal_id:
                domain.append(('journal_id', '=', journal_bank.journal_id.id))
        data_fourn = self.env['account.payment'].search(domain)
        for d in data_fourn:
            type_added = False
            date = d.date.strftime('%Y-%m-%d')
            if len(final_list) != 0:
                for line in final_list:
                    if line[0] == date:
                        index_bank = index_fourn
                        index_line = final_list.index(line)
                        line[index_bank] = round(d.amount, 2) + line[index_bank]
                        final_list[index_line] = line
                        type_added = True
                        break
            if not type_added:
                sub_line = []
                sub_line.append(date)
                for i in range(len(headers) - 1):
                    sub_line.append(0)
                index = index_fourn
                sub_line[index] = round(d.amount, 2)
                final_list.append(sub_line)
        print(5)
        index_fourn = headers.index('G50 en circulation')
        domain = [('state', '=', 'draft'), ('partner_type', '=', 'supplier'), ('autre_type', '=', 'g50')]
        if dateStart:
            domain.append(('date', '>=', dateStart))
        else:
            domain.append(('date', '!=', False))
        if dateEnd:
            domain.append(('date', '<=', dateEnd))
        else:
            domain.append(('date', '!=', False))
        if bank:
            journal_bank = self.env['credit.banque'].search([('id', '=', int(bank))])
            if journal_bank.journal_id:
                domain.append(('journal_id', '=', journal_bank.journal_id.id))
        data_fourn = self.env['account.payment'].search(domain)
        for d in data_fourn:
            type_added = False
            date = d.date.strftime('%Y-%m-%d')
            if len(final_list) != 0:
                for line in final_list:
                    if line[0] == date:
                        index_bank = index_fourn
                        index_line = final_list.index(line)
                        line[index_bank] = round(d.amount, 2) + line[index_bank]
                        final_list[index_line] = line
                        type_added = True
                        break
            if not type_added:
                sub_line = []
                sub_line.append(date)
                for i in range(len(headers) - 1):
                    sub_line.append(0)
                index = index_fourn
                sub_line[index] = round(d.amount, 2)
                final_list.append(sub_line)
        print(6)
        index_total = headers.index('Solde Banque')
        sorted_data = sorted(final_list, key=lambda x: x[0])
        banque_id = self.env['credit.banque'].search([('id', '=', bank)])
        journal_solde = banque_id.journal_id._get_journal_dashboard_outstanding_payments()
        print('journal_solde', journal_solde)
        last_total = journal_solde[banque_id.journal_id.id][1]
        for line in sorted_data:
            positif = line[1:index_client+1]
            negatif = line[index_client+1:index_total]
            total = sum(positif) - sum(negatif) + last_total
            line[index_total] = round(total, 2)
            last_total = total
        sorted_dict = []
        for index, line in enumerate(sorted_data):
            global_index = 'line_' + str(index)
            element = {
                'key': global_index,
            }
            value = []
            for sub_index, sub_line in enumerate(line):
                el = {
                    'key': global_index + '_' + str(sub_index),
                    'value': '{0:,.2f}'.format(sub_line) if sub_index != 0 else sub_line
                }
                value.append(el)
            element['value'] = value
            sorted_dict.append(element)
        print(sorted_dict)
        return sorted_dict

    @api.model
    def index_header_red(self,dateEnd, bank=1):
        dateStart = fields.Date.today()
        if not dateEnd:
            dateEnd = fields.Date.today() + timedelta(days=30)
        headers = self.get_header(dateEnd, bank)
        index_red = 0
        for index, header in enumerate(headers):
            for cle, valeur in header.items():
                if valeur == 'Chèque clients en circulation':
                    index_red = index
        header_red = headers[:index_red + 1]
        print(header_red)
        return header_red

    @api.model
    def index_header_green(self, dateEnd, bank=1):
        dateStart = fields.Date.today()
        if not dateEnd:
            dateEnd = fields.Date.today() + timedelta(days=30)
        headers = self.get_header(dateEnd, bank)
        index_red = 0
        for index, header in enumerate(headers):
            for cle, valeur in header.items():
                if valeur == 'Chèque clients en circulation':
                    index_red = index
        header_red = headers[index_red+1:]
        print(header_red)
        return header_red
