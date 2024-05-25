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
        'credit.type', string='Ligne de crédit', index=True, tracking=True, required=True, readonly=True,)
    currency_id = fields.Many2one(
        'res.currency', string="Devise", company_dependent=True, default='base.DZD',
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    montant_disponible = fields.Float(string="Disponible", store=True, )
    ligne_autorisation = fields.Many2one('credit.autorisation', string='Autorisation',
                                         readonly=True, ondelete='cascade')
    montant_autorisation = fields.Float(string="Autorisation", compute='_compute_montant', store=True, readonly=True)
    montant_difference = fields.Float(string="Montant Debloqué", compute='_compute_montant_diff', store=True)
    debloque = fields.One2many('credit.operation.deb', 'disponible_id', string='Opération de déblocage', )

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

            autorisations = rec.env['credit.autorisation'].search([])
            print('autorisations = ',autorisations)

            for auto in autorisations:
                qsdeb = rec.env['credit.operation.deb'].search([('ligne_autorisation.banque.id', '=', auto.banque.id),
                                                         ('ligne_autorisation.type', '=', auto.type.id)])
                m = auto.montant
                print('qsdeb = ', qsdeb)
                for q in qsdeb:
                    m = m - q.montant_debloque

                qsp = rec.env['credit.operation.p'].search([('ref_opr_deb.ligne_autorisation.banque', '=', auto.banque.id),
                                                             ('ref_opr_deb.ligne_autorisation.type', '=', auto.type.id)])
                print('qsp = ', qsp)
                for q in qsp:
                    m = m + q.montant_paye

                disponibles = rec.env['credit.disponible'].search([])
                print('disponibles = ', disponibles)
                for disponible in disponibles:
                    if auto.id == disponible.ligne_autorisation.id:
                        disponible.montant_disponible = m
                        print(disponible.montant_disponible)

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
    def _get_solde(self):
        somme = 0
        header = self._prepare_modif()
        solde_list = ['']
        for h in header[1:]:
            somme = 0
            banque_id = self.env['credit.banque'].search([('name', '=', h)])
            journ = banque_id.journal_id._get_journal_dashboard_outstanding_payments()
            print(journ)
            print(journ[banque_id.journal_id.id][1])
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
