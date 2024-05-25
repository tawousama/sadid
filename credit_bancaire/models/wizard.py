import datetime

from odoo import api, fields, models, _
from datetime import datetime

class Wizard(models.TransientModel):
    _name = 'wizard.credit.deblocage'

    def send(self):
        print(self.env.context.get('deblocage'))
        if self.env.context.get('deblocage'):
            deblocage = self.env['credit.operation.deb'].browse(self.env.context.get('deblocage'))
            print(deblocage)
            self.env['account.payment'].create({'payment_type': 'inbound',
                                                'amount': deblocage.montant_debloque,
                                                'journal_id': deblocage.banque_id.journal_id.id,
                                                'date': deblocage.deblocage_date,
                                                'ref': deblocage.name})
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'type': 'success',
                'sticky': False,
                'message': _('Compte credité avec succés')})
        if self.env.context.get('payment'):
            payment = self.env['credit.operation.p'].browse(self.env.context.get('payment'))
            print(payment)
            self.env['account.payment'].create({'payment_type': 'outbound',
                                                'amount': payment.montant_echeance,
                                                'date': datetime.datetime.today(),
                                                'journal_id': payment.banque.journal_id.id,
                                                'partner_type': 'supplier',
                                                'ref': payment.name})
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'type': 'success',
                'sticky': False,
                'message': _('Compte debité avec succés'),

            })
            if self.env.context.get('deb_id'):
                print('deblocage', self.env.context.get('deb_id'))
                echeance = self.env['credit.echeance'].search([('ref_opr_deb', '=', self.env.context.get('deb_id'))])
                if echeance:
                    print(echeance.state)
                    echeance.state = 'paid'

    def cancel(self):
        if self.env.context.get('deb_id'):
            print('deblocage', self.env.context.get('deb_id'))
            echeance = self.env['credit.echeance'].search([('ref_opr_deb', '=', self.env.context.get('deb_id'))])
            if echeance:
                print(echeance.state)
                echeance.state = 'paid'
        return {'type': 'ir.actions.act_window_close'}


class WizardEndettement(models.TransientModel):
    _name = 'wizard.credit.endettement'

    def send(self):
        dispo = self.env['credit.disponible'].search([], limit=1)
        return self.env.ref('credit_bancaire.endettement_report').report_action(dispo)

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class BudgetRequest(models.Model):
    _name = 'budget.request'

    name = fields.Char()
    start_date = fields.Date(string='Date debut')
    end_date = fields.Date(string='Date fin')
    amount = fields.Float(string='Montant')
    description = fields.Text(string='Commentaire')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Département')
    state = fields.Selection([('send', 'Envoyé'),
                              ('deleted', 'Annulé')], default='send',
                             string='Etat')


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[('draft', 'En circulation')])


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    date_encaissement = fields.Date(string='Date prévue d\'encaissement')
    date_decaissement = fields.Date(string='Date prévue de decaissement')

    @api.model
    def get_time_off(self, dateStart, dateEnd):
        domain = [('state', '=', 'draft'), ('partner_type', '=', 'customer')]
        if dateStart:
            date_start = datetime.strptime(dateStart, "%Y-%m-%d")

            domain.append(('date', '>=', date_start))
        if dateEnd:
            date_end = datetime.strptime(dateEnd, "%Y-%m-%d")
            domain.append(('date', '<=', date_end))
        data = self.env['account.payment'].search(domain)
        headers = self.get_header(dateStart, dateEnd)
        final_list = []
        for d in data:
            type_added = False
            date = d.date.strftime('%Y-%m-%d')
            if len(final_list) != 0:
                for line in final_list:
                    if line[0] == date:
                        index_bank = headers.index(d.journal_id.name)
                        index_line = final_list.index(line)
                        line[index_bank] = d.amount_signed + line[index_bank]
                        final_list[index_line] = line
                        type_added = True
                        break
            if not type_added:
                sub_line = []
                sub_line.append(date)
                for i in range(len(headers) - 1):
                    sub_line.append(0)
                index = headers.index(d.journal_id.name)
                sub_line[index] = d.amount_signed
                final_list.append(sub_line)
        for line in final_list:
            total = sum(line[1:])
            line[-1] = total
        paiement_clients = ['Paiement clients']
        for i in range(len(headers) - 1):
            paiement_clients.append(0)
        for row in final_list:
            row_value = row[1:]
            for index, item in enumerate(row_value):
                paiement_clients[index + 1] += item
        final_list.insert(0, paiement_clients)
        return final_list

    @api.model
    def get_total(self, dateStart, dateEnd):
        final_list = ['Total']
        customer_list = self.get_time_off(dateStart, dateEnd)

        customer = [row for row in customer_list if row[0] == 'Paiement clients'][0][1:]
        supplier_list = self.get_supplier_off(dateStart, dateEnd)
        supplier = [row for row in supplier_list if row[0] == 'Paiement fournisseurs'][0][1:]
        for index, item in enumerate(customer):
            item = item + supplier[index]
            final_list.append(item)
        return final_list

    @api.model
    def get_supplier_off(self, dateStart, dateEnd):
        domain = [('state', '=', 'draft'), ('partner_type', '=', 'supplier')]
        if dateStart:
            date_start = datetime.strptime(dateStart, "%Y-%m-%d")

            domain.append(('date', '>=', date_start))
        if dateEnd:
            date_end = datetime.strptime(dateEnd, "%Y-%m-%d")
            domain.append(('date', '<=', date_end))
        data = self.env['account.payment'].search(domain)
        headers = self.get_header(dateStart, dateEnd)
        final_list = []
        for d in data:
            type_added = False
            date = d.date.strftime('%Y-%m-%d')
            if len(final_list) != 0:
                for line in final_list:
                    if line[0] == date:
                        index_bank = headers.index(d.journal_id.name)
                        index_line = final_list.index(line)
                        line[index_bank] = d.amount_signed + line[index_bank]
                        final_list[index_line] = line
                        type_added = True
                        break
            if not type_added:
                sub_line = []
                sub_line.append(date)
                for i in range(len(headers) - 1):
                    sub_line.append(0)
                index = headers.index(d.journal_id.name)
                sub_line[index] = d.amount_signed
                final_list.append(sub_line)
        for line in final_list:
            total = sum(line[1:])
            line[-1] = total
        paiement_clients = ['Paiement fournisseurs']
        for i in range(len(headers) - 1):
            paiement_clients.append(0)
        for row in final_list:
            row_value = row[1:]
            for index, item in enumerate(row_value):
                paiement_clients[index + 1] += item
        final_list.insert(0, paiement_clients)
        return final_list

    @api.model
    def get_header(self, dateStart, dateEnd):
        domain = [('state', '=', 'draft')]
        if dateStart:
            date_start = datetime.strptime(dateStart, "%Y-%m-%d")
            domain.append(('date', '>=', date_start))
        if dateEnd:
            date_end = datetime.strptime(dateEnd, "%Y-%m-%d")
            domain.append(('date', '<=', date_end))
        domain = [('state', '=', 'draft')]
        data = self.env['account.payment'].search(domain)
        headers = ['Date']
        for d in data:
            if d.journal_id.name not in headers:
                headers.append(d.journal_id.name)
        headers.append('Total')
        return headers
