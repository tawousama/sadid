import json

from odoo import api, fields, models, _


class Gestion_disponible(models.Model):
    _name = 'credit.disponible'
    _description = "Lignes disponibles par banque "

    name = fields.Char(string='Disponibles', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    banque = fields.Many2one(
        'credit.banque', string='Banque', index=True, tracking=True, required=True, readonly=True,)
    type = fields.Many2one(
        'credit.type', string='Ligne de crédit', index=True, tracking=True, readonly=True,)
    type_ids = fields.Many2many(
        'credit.type', string='Ligne de crédit', index=True, tracking=True, required=True)

    currency_id = fields.Many2one(
        'res.currency', string="Devise", company_dependent=True, default='base.DZD',
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    montant_disponible = fields.Float(string="Disponible", store=True, )
    ligne_autorisation = fields.Many2one('credit.autorisation', string='Autorisation',
                                         readonly=True, ondelete='cascade')
    montant_autorisation = fields.Float(string="Autorisation", compute='_compute_montant', store=True, readonly=True)
    montant_difference = fields.Float(string="Montant Debloqué", compute='_compute_montant_diff', store=True)
    comment = fields.Text(string='Commentaire')
    date_report = fields.Date(string='Date')
    debloque_ids = fields.One2many('credit.operation.deb', 'disponible_id', string='Opération de déblocage')
    has_deblocage = fields.Boolean(compute='get_debloque')
    echeance_ids = fields.One2many('credit.echeance', 'disponible_id', string='Opération d\'echeances')
    has_echeance = fields.Boolean(compute='get_echeance')

    def get_debloque(self):
        for rec in self:
            debloque_ids = self.env['credit.operation.deb'].search([('ligne_autorisation', '=', rec.ligne_autorisation.id),
                                                                    ('state', '!=', 'draft')])
            if debloque_ids:
                for deb in debloque_ids:
                    deb.disponible_id = rec.id
                rec.has_deblocage = True
            else:
                rec.has_deblocage = False

    def get_echeance(self):
        for rec in self:
            echeance_ids = self.env['credit.echeance'].search([('ligne_autorisation', '=', rec.ligne_autorisation.id),
                                                               ('state', '=', 'paid')])
            echeance_paid_ids = self.env['credit.echeance'].search([('ligne_autorisation', '=', rec.ligne_autorisation.id),
                                                                ('state', '!=', 'paid')])
            if echeance_ids:
                for ech in echeance_ids:
                    ech.disponible_id = rec.id
                rec.has_echeance = True
            else:
                rec.has_echeance = False
            if echeance_paid_ids:
                for ech in echeance_paid_ids:
                    ech.disponible_id = False

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.disponible') or _('New')

        result = super(Gestion_disponible, self).create(vals)
        return result

    @api.model
    def write(self, vals):
        result = super(Gestion_disponible, self).write(vals)
        return result

    def action_MAJ(self):
        for rec in self:
            total_autorisation = rec.montant_autorisation
            dispo = 0
            total_deb = 0
            total_ech = 0
            if "Découvert" not in rec.ligne_autorisation.type_ids.mapped('titre'):
                if rec.has_deblocage:
                    total_deb = sum(rec.debloque_ids.mapped('montant_rembourser'))
                if rec.has_echeance:
                    total_ech = sum(rec.echeance_ids.mapped('montant_a_rembourser'))
                dispo = total_autorisation - total_deb + total_ech
                rec.montant_disponible = dispo
            else:
                if rec.banque.journal_id:
                    journal = rec.banque.journal_id
                    journ = journal._get_journal_dashboard_outstanding_payments()
                    if journ:
                        total_deb = journ[journal.id][1]
                    dispo = total_autorisation - total_deb
            rec.montant_disponible = dispo

    @api.depends('ligne_autorisation')
    def _compute_montant(self):
        for rec in self:
            rec.montant_autorisation = rec.ligne_autorisation.montant

    @api.depends('montant_autorisation', 'montant_disponible')
    def _compute_montant_diff(self):
        for rec in self:
            rec.montant_difference = rec.montant_autorisation - rec.montant_disponible

    @api.model
    def _prepare_modif(self):
        final_list = []
        header_list = ['']
        deblocage_ids = self.env['credit.disponible'].search([])
        if deblocage_ids:
            for deb in deblocage_ids:
                if deb.banque.name not in header_list:
                    header_list.append(deb.banque.name)
            for deb in deblocage_ids:
                type_added = False
                if len(final_list) != 0:
                    for line in final_list:
                        if line[0] == deb.type.name:
                            index_bank = header_list.index(deb.banque.name)
                            index_line = final_list.index(line)
                            line[index_bank] = deb.montant_difference + line[index_bank]
                            final_list[index_line] = line
                            type_added = True
                            break
                if not type_added:
                    sub_line = []
                    sub_line.append(deb.type.name)
                    for i in range(len(header_list) - 1):
                        sub_line.append(0)
                    index = header_list.index(deb.banque.name)
                    sub_line[index] = deb.montant_difference
                    final_list.append(sub_line)

        return header_list

    @api.model
    def _prepare_body(self):
        final_list = []
        header_list = ['']
        deblocage_ids = self.env['credit.disponible'].search([])
        if deblocage_ids:
            for deb in deblocage_ids:
                if deb.banque.name not in header_list:
                    header_list.append(deb.banque.name)
            for deb in deblocage_ids:
                type_added = False
                if len(final_list) != 0:
                    for line in final_list:
                        if line[0] == deb.type.name:
                            index_bank = header_list.index(deb.banque.name)
                            index_line = final_list.index(line)
                            line[index_bank] = deb.montant_difference + line[index_bank]
                            final_list[index_line] = line
                            type_added = True
                            break
                if not type_added:
                    sub_line = []
                    sub_line.append(deb.type.name)
                    for i in range(len(header_list) - 1):
                        sub_line.append(0)
                    index = header_list.index(deb.banque.name)
                    sub_line[index] = deb.montant_difference
                    final_list.append(sub_line)

        return final_list

    @api.model
    def _get_tresorerie(self):
        somme = 0
        header = self._prepare_modif()
        tres_list = ['']
        for h in header[1:]:
            somme = 0
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            tresorerie = self.env['credit.disponible'].search([('type', 'not in', [4, 10, 11, 12]),
                                                               ('banque', '=', banque_id.id)])
            if tresorerie:
                somme = sum(tresorerie.mapped('montant_difference'))
            tres_list.append(somme)
        return tres_list

    @api.model
    def _get_signature(self):
        somme = 0
        header = self._prepare_modif()
        signature_list = ['']
        for h in header[1:]:
            somme = 0
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            tresorerie = self.env['credit.disponible'].search([('type', 'in', [4]),
                                                               ('banque', '=', banque_id.id)])
            if tresorerie:
                somme = sum(tresorerie.mapped('montant_difference'))
            signature_list.append(somme)
        return signature_list

    @api.model
    def _get_taux(self):
        header = self._prepare_modif()
        signature_list = []
        for h in header[1:]:
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            autorisation = self.env['credit.autorisation_global'].search([('banque', '=', banque_id.id)])
            if autorisation:
                signature_list.append(autorisation.taux)
        return signature_list

    @api.model
    def _get_taux_total(self):
        total = self._get_taux()
        try:
            taux = sum(total) / len(total)
        except:
            taux = 0
        return taux

    @api.model
    def _get_total_eng(self):
        total = self._get_total_engagement()
        try:
            taux = sum(total)
        except:
            taux = 0
        return taux

    @api.model
    def _get_total_deblo(self):
        total = self._get_total_deb()
        try:
            taux = sum(total)
        except:
            taux = 0
        return taux

    @api.model
    def _get_total_deblo_ratio(self):
        tot = self._get_total_eng()
        total = self._get_total_deblo()
        print('tot', tot)
        print('total', total)
        try:
            taux = total / tot
        except:
            taux = 0
        return taux

    @api.model
    def _get_total_engagement(self):
        header = self._prepare_modif()
        signature_list = []
        for h in header[1:]:
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            autorisation = self.env['credit.autorisation_global'].search([('banque', '=', banque_id.id)])
            if autorisation:
                somme = sum(autorisation.ligne_autorisation.mapped('montant'))
                signature_list.append(somme)
        return signature_list

    @api.model
    def _get_total_deb(self):
        header = self._prepare_modif()
        signature_list = []
        for h in header[1:]:
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            deb = self.env['credit.operation.deb'].search([('banque_id', '=', banque_id.id)])
            if deb:
                somme = sum(deb.mapped('montant_debloque'))
                signature_list.append(somme)

        return signature_list

    @api.model
    def _get_echeances(self):
        header = self._prepare_modif()
        signature_list = []
        for h in header[1:]:
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            echeance = self.env['credit.echeance'].search([('banque', '=', banque_id.id), ('echeance_date', '!=', False)])
            if echeance:
                sorted_echeance = sorted(echeance.mapped('echeance_date'))
                print(sorted_echeance)
                signature_list.append(sorted_echeance[0])
            else:
                signature_list.append('-')
        return signature_list

    @api.model
    def _get_total_deb_ratio(self):
        header = self._prepare_modif()

        signature_list = []
        for h in header[1:]:
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            deb = self.env['credit.operation.deb'].search([('banque_id', '=', banque_id.id)])
            autorisation = self.env['credit.autorisation_global'].search([('banque', '=', banque_id.id)])
            if deb:
                total_aut = sum(autorisation.ligne_autorisation.mapped('montant'))
                somme = sum(deb.mapped('montant_debloque'))
                ratio = somme / total_aut if total_aut != 0 else 0
                signature_list.append(ratio)

        return signature_list

    @api.model
    def _get_solde(self):
        somme = 0
        header = self._prepare_modif()
        solde_list = ['']
        for h in header[1:]:
            somme = 0
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            journ = banque_id.journal_id._get_journal_dashboard_outstanding_payments()
            print(journ)
            #print(journ[banque_id.journal_id.id][1])
            if journ:
                somme = journ[banque_id.journal_id.id][1]
            solde_list.append(somme)
        return solde_list

    @api.model
    def _get_endettement(self):
        somme = 0
        header = self._prepare_modif()
        endettement_list = ['']
        endettement_ids = self.env['credit.disponible'].search([])
        endettement = sum(endettement_ids.mapped('montant_difference'))
        for h in header[1:]:
            somme = 0
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            tresorerie = self.env['credit.disponible'].search([('banque', '=', banque_id.id)])
            if tresorerie:
                somme = sum(tresorerie.mapped('montant_difference')) / endettement if endettement != 0 else 0
            endettement_list.append(somme)
        return endettement_list
