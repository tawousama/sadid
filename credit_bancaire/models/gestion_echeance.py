from odoo import api, fields, models, _


class Gestion_echeance(models.Model):
    _name = 'credit.echeance'
    _inherit = ["mail.thread",'mail.activity.mixin']
    _description = "Échéances a venir"

    name = fields.Char(string='Opération', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    ref_opr_deb = fields.Many2one('credit.operation.deb', string='Opération de déblocage',ondelete='cascade')
    banque = fields.Many2one(
        'credit.banque', string='Banque', index=True, tracking=True, )
    type = fields.Many2one(
        'credit.type', string='Ligne de crédit', index=True, tracking=True)

    echeance_date = fields.Date("Date d`échéance", tracking=True)
    montant_a_rembourser = fields.Float(string="Montant à rembourser", store=True)
    currency_id = fields.Many2one(
        'res.currency', string="Devise", company_dependent=True, default='base.DZD',
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    fournisseur = fields.Many2one('res.partner', string='Client / Fournisseur', index=True, tracking=True)
    facture = fields.Many2one('account.move', string='N. facture', tracking=True)
    echeance = fields.Many2one('credit.operation.deb.echeance', string='echeance partiel',index=True, tracking=True,store=True, ondelete="cascade")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.operation') or _('New')
        id= self.id
        print('id de lecheance'+str(id))
        result = super(Gestion_echeance, self).create(vals)
        return result

    def action_ech_MAJ(self):
        for rec in self:
            debs = rec.env['credit.operation.deb'].search([])
            for deb in debs:
                q = self.env['credit.echeance'].search([('name', '=', deb.name)])
                if q :
                    q.echeance_date = deb.echeance_date
                    q.montant_debloque = deb.montant_debloque


