import datetime

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta

class Gestion_autorisation(models.Model):
    _name = 'credit.autorisation'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Autorisation des lignes de crédit bancaire"

    name = fields.Char(string='Autorisation', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    banque = fields.Many2one(
        'credit.banque', string='Banque', index=True, tracking=True, related="autorisation_global.banque",store=True)
    type = fields.Many2one(
        'credit.type', string='Ligne de crédit', index=True, tracking=True, required=True)
    currency_id = fields.Many2one(
        'res.currency', string="Devise", company_dependent=True, default='base.DZD',
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    montant = fields.Float(string="Montant de l`autorisation", store=True, required=True)
    condition_objet = fields.Text(string="Objet et Conditions", store=True, required=True)
    date_create = fields.Datetime(string='Date de création', required=True, index=True, copy=False,
                                 default=fields.Datetime.now,
                                 help="Indicates the date the autorisation was created.",
                                 readonly=True)
    validite = fields.Date("Validité de la ligne", tracking=True, required=True)
    date_limit = fields.Date("Date limite", tracking=True, required=True)
    validite_due = fields.Date("Vérification de la date", tracking=True,default=fields.Datetime.now)
    condition = fields.Char(string='Condition non bloquante a réaliser', tracking=True)
    rappel = fields.Date("Date de rappel de renouvellement", tracking=True, store=True)
    user_id = fields.Many2one(
        'res.users', string='Order representative', index=True, tracking=True, readonly=True,
        default=lambda self: self.env.user, check_company=True)
    autorisation_global = fields.Many2one('credit.autorisation_global', ondelete='cascade', string='Autorisation global')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.autorisation') or _('New')
        result = super(Gestion_autorisation, self).create(vals)
        return result

    @api.depends('autorisation_global')
    def _compute_banque(self):
        for rec in self:
            rec.banque = rec.autorisation_global.banque


    @api.depends('validite')
    def _compute_date(self):
        for rec in self:
            if rec.validite:
                rec.validite_due = rec.validite
                #rec.rappel = datetime.datetime.strptime(str(rec.validite), '%Y-%m-%d') - relativedelta(days=+ 7)

class Autorisation_global(models.Model):
    _name = 'credit.autorisation_global'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Ensemble des autorisations des lignes de crédit bancaire"

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.autorisation_global') or _('New')

        result = super(Autorisation_global, self).create(vals)
        return result

    name = fields.Char(string='Ensemble d`autorisations', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    banque = fields.Many2one(
        'credit.banque', string='Banque', index=True, tracking=True, required=True)
    ligne_autorisation = fields.One2many('credit.autorisation', 'autorisation_global', string="ligne d`autorisation")
    taux = fields.Float(string='Taux')
    file_ticket = fields.Binary(string='Ticket d`Autorisation')
    file_name = fields.Char(string='File name')

    @api.depends('banque')
    def action_Disponible(self):
        for record in self:
            for aut in record.ligne_autorisation:
                q = aut.env['credit.disponible'].search([('ligne_autorisation', '=', aut.id)])
                print(q)
                val = {
                    'montant_disponible': aut.montant,
                    'ligne_autorisation': aut.id,
                    'banque': record.banque.id,
                    'type': aut.type.id,
                }
                if not q:
                    aut.env['credit.disponible'].create(val)