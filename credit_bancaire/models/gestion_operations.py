from odoo import api, fields, models, _


class Gestion_operation(models.Model):
    _name = 'credit.operation'
    _inherit = ["mail.thread",'mail.activity.mixin']
    _description = "Opérations bancaire"

    name = fields.Char(string='Opération', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    banque = fields.Many2one(
        'credit.banque', string='Banque', index=True, tracking=True)
    type = fields.Many2one(
        'credit.type', string='Ligne de crédit', index=True, tracking=True)
    montant_debloque = fields.Float(string="Montant débloqué", store=True)
    montant_rembourser= fields.Float(string="Montant a rembourser", store=True)
    montant_paye = fields.Float(string="Montant payé", store=True)
    deblocage_date = fields.Date("Date de déblocage", tracking=True)
    echeance_date = fields.Date("Date d`échéance", tracking=True)
    echeance_date_new = fields.Date("Nouvelle date d`échéance", tracking=True)
    note = fields.Text(string='Description', tracking=True)
    capital_interet = fields.Char(string='Capital / interet', tracking=True)
    referene_credit = fields.Char(string='Référene du dossier banque', tracking=True)
    #referene_interne = fields.Char(string='Référence interne (N. facture)', tracking=True)
    referene_interne = fields.Many2one('account.move', string='Référence interne (N. facture)',  tracking=True)

    user_id = fields.Many2one(
        'res.users', string='Order representative', index=True, tracking=True, readonly=True,
        default=lambda self: self.env.user, check_company=True)
    partner = fields.Many2one('res.partner', string='Client / Fournisseur', index=True, tracking=True)
    paiement = fields.Boolean('paiement.xml', default=False)
    prorogation = fields.Boolean('prorogation', default=False)

    ligne_autorisation = fields.Many2one('credit.autorisation', string='Autorisation', compute='_compute_autorisation', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.operation') or _('New')

        result = super(Gestion_operation, self).create(vals)
        return result

    def _compute_autorisation(self):
        for rec in self:
            rec.ligne_autorisation = rec.env['credit.autorisation'].search([('banque', '=', rec.banque), ('type', '=', rec.type)])

            print(rec.ligne_autorisation)
            # rec.purchase_order_count = 0

