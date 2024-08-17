import datetime

from odoo import api, fields, models, _
from datetime import datetime, timedelta

class Wizard(models.TransientModel):
    _name = 'wizard.credit.deblocage'

    def send(self):
        print(self.env.context.get('deblocage'))
        if self.env.context.get('deblocage'):
            deblocage = self.env['credit.operation.deb'].browse(self.env.context.get('deblocage'))
            print(deblocage)
            deb_payment = self.env['account.payment'].create({'payment_type': 'inbound',
                                                'amount': deblocage.montant_debloque,
                                                'partner_id': deblocage.banque_id.partner_id.id,
                                                'journal_id': deblocage.banque_id.journal_id.id,
                                                'date': deblocage.deblocage_date,
                                                'ref': deblocage.name})
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'type': 'success',
                'sticky': False,
                'message': _('Compte credité avec succés')})
            view_id = self.env.ref('account.view_account_payment_form').id
            return {
                'type': 'ir.actions.act_window',
                'name': _('Paiement'),
                'view_mode': 'form',
                'res_model': 'account.payment',
                'target': 'new',
                'view_id': view_id,
                'res_id': deb_payment.id,
            }
        if self.env.context.get('payment'):
            payment = self.env['credit.echeance'].browse(self.env.context.get('payment'))
            print(payment)
            payment = self.env['account.payment'].create({'payment_type': 'outbound',
                                                'amount': payment.montant_a_rembourser,
                                                'date': datetime.today(),
                                                'journal_id': payment.banque.journal_id.id,
                                                'partner_type': 'supplier',
                                                'type_supplier': 'local',
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
            view_id = self.env.ref('account.view_account_payment_form').id
            return {
                'type': 'ir.actions.act_window',
                'name': _('Paiement'),
                'view_mode': 'form',
                'res_model': 'account.payment',
                'target': 'new',
                'view_id': view_id,
                'res_id': payment.id,
            }
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

    comment = fields.Text(string='Commentaire')
    date_report = fields.Date(string='Date')

    def send(self):
        self.ensure_one()
        dispo = self.env['credit.disponible'].search([], limit=1)
        dispo.comment = self.comment
        dispo.date_report = self.date_report
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

    ref_supplier = fields.Char(string='Numéro de cheque')
    date_encaissement_dec = fields.Date(string='Date prévue d\'encaissement', store=True)
    autre_type = fields.Selection(selection=[('salaire', 'Salaire'),
                                             ('g50', 'G50'),
                                             ('provision', 'Provision LC')])
    state_payment = fields.Selection([('draft', 'En cours'),
                                      ('posted', 'Comptabilisé'),
                                      ('cancel', 'Annulé')], default='draft', string='Statut', compute='_compute_state_autre', store=True)

    date_echeance = fields.Date(string='Date d\'échéance')
    date_ddl_depot = fields.Date(string='Date de dépôt de virement au plus tard')
    date_debit = fields.Date(string='Date de débit')
    date_valeur = fields.Date(string='Date de valeur')
    month = fields.Selection([('1', 'Janvier'),
                              ('2', 'Fevrier'),
                              ('3', 'Mars'),
                              ('4', 'Avril'),
                              ('5', 'Mai'),
                              ('6', 'Juin'),
                              ('7', 'Juillet'),
                              ('8', 'Aout'),
                              ('9', 'Septembre'),
                              ('10', 'Octobre'),
                              ('11', 'Novembre'),
                              ('12', 'Decembre')], string='Mois')
    year = fields.Char(string='Année', size=4)
    type_supplier = fields.Selection([('local', 'Local'),
                                      ('etranger', 'Etranger')], string='Type de fournisseur',)
    payment_mode = fields.Selection(selection=[('cheque', 'Chèque'),
                ('virement', 'Virement'),
                ('carte', 'Carte Bancaire'),
                ('bank_cheque', 'Chèque de Banque')], string='Mode de Paiement')
    payment_mode_client = fields.Selection(selection=[('cheque', 'Chèque'),
                ('virement', 'Virement'),
                ('bank_cheque', 'Chèque de Banque')], string='Mode de Paiement')
    carte_id = fields.Many2one('account.card', string='Carte Bancaire')
    payment_mode_et = fields.Selection([('remdoc', 'REMDOC'),
                                        ('lc_vue', 'LC à VUE'),
                                        ('lc_dp', 'LC à DP'),
                                        ('transfert', 'Transfert Libre')], string='Mode de Paiement')
    date_cheque = fields.Date(string='Date de remise de chèque')
    accuse_par = fields.Selection([('beneficiaire', 'Bénéficiaire'),
                                   ('intermediaire', 'Intermediaire')], string='Accusé par')
    dept_id = fields.Many2one('hr.department', string='Service demandeur')
    comment = fields.Text(string='Commentaire')

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        if res.partner_type == 'customer':
            res.date_encaissement_dec = fields.Date.today() + timedelta(days=5)
        elif res.partner_type == 'supplier':
            res.date_encaissement_dec = fields.Date.today() + timedelta(days=1)
        return res

    @api.depends('partner_type')
    def _compute_date_encaissement(self):
        for rec in self:
            if rec.partner_type == 'customer':
                rec.date_encaissement_dec = fields.Date.today() + timedelta(days=5)
            elif rec.partner_type == 'supplier':
                rec.date_encaissement_dec = fields.Date.today() + timedelta(days=1)
            print('rec.date_encaissement_dec', rec.date_encaissement_dec)

    @api.depends('state')
    def _compute_state_autre(self):
        for rec in self:
            print('rec')
            rec.state_payment = rec.state

    @api.model
    def get_time_off(self):
        print(1)
        domain = [('state', '=', 'draft'), ('partner_type', '=', 'customer'), ('date_encaissement_dec', '!=', False)]
        data = self.env['account.payment'].search(domain)
        print(2)
        headers = self.get_header()
        print(3)
        final_list = []
        for d in data:
            type_added = False
            date = d.date_encaissement_dec.strftime('%Y-%m-%d')
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
        sorted_data = sorted(final_list, key=lambda x: x[0])
        sorted_dict = []
        for index, line in enumerate(sorted_data):
            sub_value = []
            for sub_index, sub_line in enumerate(line):
                value = '{0:,.2f}'.format(sub_line) if sub_index != 0 else sub_line
                sub_value.append(value)
            sorted_dict.append(sub_value)
        return sorted_dict

    @api.model
    def get_total(self):
        final_list = ['Total']
        customer_list = self.get_time_off()
        customer = [row for row in customer_list if row[0] == 'Paiement clients'][0][1:]
        supplier_list = self.get_supplier_off()
        supplier = [row for row in supplier_list if row[0] == 'Paiement fournisseurs'][0][1:]
        for index, item in enumerate(customer):
            customer_item = item.replace(',', '')
            supplier_item = supplier[index].replace(',', '')
            item = float(customer_item) + float(supplier_item)
            final_list.append(item)
        sorted_dict = []
        for index, line in enumerate(final_list):
            try:
                value = '{0:,.2f}'.format(line)
            except:
                value = line
            sorted_dict.append(value)
        return sorted_dict

    @api.model
    def get_supplier_off(self):
        domain = [('state', '=', 'draft'), ('partner_type', '=', 'supplier'), ('date_encaissement_dec', '!=', False)]
        data = self.env['account.payment'].search(domain)
        headers = self.get_header()
        final_list = []
        for d in data:
            type_added = False
            date = d.date_encaissement_dec.strftime('%Y-%m-%d')
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
        sorted_data = sorted(final_list, key=lambda x: x[0])
        sorted_dict = []
        for index, line in enumerate(sorted_data):
            sub_value = []
            for sub_index, sub_line in enumerate(line):
                value = '{0:,.2f}'.format(sub_line) if sub_index != 0 else sub_line
                sub_value.append(value)
            sorted_dict.append(sub_value)
        return sorted_dict

    @api.model
    def get_header(self):
        domain = [('state', '=', 'draft'), ('date_encaissement_dec', '!=', False)]
        data = self.env['account.payment'].search(domain)
        headers = ['Date']
        for d in data:
            if d.journal_id.name not in headers:
                headers.append(d.journal_id.name)
        headers.append('Total')
        return headers


class Partner(models.Model):
    _inherit = 'res.partner'

    nif = fields.Char(string='NIF')
    rc = fields.Char(string='RC')
    nis = fields.Char(string='NIS')
    swift = fields.Char(string='SWIFT')
    bank_address = fields.Char(string='Adresse de la banque')
    cart_ids = fields.One2many('account.card', 'partner_id', string='Cartes bancaire')
    partner_type = fields.Selection([('customer', 'Client'),
                                     ('supplier', 'Fournisseur')])
    supplier_type = fields.Selection([('local', 'Local'),
                                      ('etranger', 'Etranger')])


class Card(models.Model):
    _name = 'account.card'

    name = fields.Char(string='Nom')
    partner_id = fields.Many2one('res.partner', string='Propriétaire', required=True)
    number_card = fields.Char(string='Numero de la carte')
    validity_date = fields.Date(string='Date d\'expiration')

    '''@api.depends('partner_id')
    def _compute_name(self):
        for rec in self:
            if rec.partner_id:
                rec.name = 'Carte Bancaire ' + rec.partner_id.name
            else:
                rec.name = 'Carte Bancaire '
            '''
    @api.model
    def create(self, vals):
        res = super(Card, self).create(vals)
        res.name = 'Carte Bancaire ' + res.partner_id.name
        return res

