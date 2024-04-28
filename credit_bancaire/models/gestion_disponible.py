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

