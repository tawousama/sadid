from datetime import datetime, timedelta

from odoo import api, fields, models, _


class Gestion_echeance(models.Model):
    _name = 'credit.echeance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Échéances a venir"

    name = fields.Char(string='Opération', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    ref_opr_deb = fields.Many2one('credit.operation.deb', string='Opération de déblocage',ondelete='cascade')
    banque = fields.Many2one(
        'credit.banque', string='Banque', index=True, tracking=True, )
    type = fields.Many2one(
        'credit.type', string='Ligne de crédit', index=True, tracking=True)
    type_ids = fields.Many2many(
        'credit.type', string='Ligne de crédit', index=True, tracking=True, related="ref_opr_deb.type_ids")

    echeance_date = fields.Date("Date d`échéance", tracking=True)
    montant_a_rembourser = fields.Float(string="Montant à rembourser", store=True)
    currency_id = fields.Many2one(
        'res.currency', string="Devise", company_dependent=True, default='base.DZD',
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    fournisseur = fields.Many2one('res.partner', string='Client / Fournisseur', index=True, tracking=True)
    facture = fields.Many2one('account.move', string='N. facture', tracking=True)
    echeance = fields.Many2one('credit.operation.deb.echeance', string='echeance partiel',index=True, tracking=True,store=True, ondelete="cascade")
    state = fields.Selection([('not_paid', 'Non payé'),
                              ('paid', 'Payé')], default='not_paid', string='Etat')
    is_retard = fields.Boolean(string='En retard')

    def validate_payment(self):
        for rec in self:
            if not rec.echeance_date:
                rec.echeance_date = fields.Date.today()
            view_id = self.env.ref('credit_bancaire.deblocage_wizard_form').id
            return {
                'name': 'Information',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'wizard.credit.deblocage',
                'view_id': view_id,
                'target': 'new',
                'context': {'payment': rec.id,
                            'deb_id': rec.ref_opr_deb.id},
            }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.operation') or _('New')
        id = self.id
        result = super(Gestion_echeance, self).create(vals)
        return result
    def action_ech_MAJ(self):
        for rec in self:
            debs = rec.env['credit.operation.deb'].search([])
            for deb in debs:
                q = self.env['credit.echeance'].search([('name', '=', deb.name)])
                if q:
                    q.echeance_date = deb.echeance_date
                    q.montant_debloque = deb.montant_debloque

    @api.model
    def reminder_thread(self):
        date = fields.Date.today() + timedelta(days=9)
        users = self.env.ref('credit_bancaire.group_credit_user').users.mapped('partner_id').mapped('email')
        mails = ', '.join(users)
        echeances = self.env['credit.echeance'].search([('echeance_date', '=', date)])
        if echeances:
            for echeance in echeances:
                print(self.env.user.partner_id.email)
                email_template = self.env.ref('credit_bancaire.reminder_mail_template')
                email_values = {
                    'email_from': self.env.user.partner_id.email,
                    'email_to': mails,
                }
                email_template.send_mail(echeance.id, force_send=True, email_values=email_values)
        date_late = fields.Date.today()
        echeances = self.env['credit.echeance'].search([('echeance_date', '<=', date_late)])
        if echeances:
            for echeance in echeances:
                echeance.is_retard = True

