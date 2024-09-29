import datetime

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class Gestion_autorisation(models.Model):
    _name = 'credit.autorisation'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Autorisation des lignes de crédit bancaire"
    _rec_name = 'display_name'

    display_name = fields.Char(string='Nom', compute='_compute_display', store=True)
    name = fields.Char(string='Autorisation', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    banque = fields.Many2one(
        'credit.banque', string='Banque', index=True, tracking=True, related="autorisation_global.banque",store=True)
    type = fields.Many2one(
        'credit.type', string='Ligne de crédit', index=True, tracking=True,)
    type_ids = fields.Many2many(
        'credit.type', string='Ligne de crédit', index=True, tracking=True, required=True)
    currency_id = fields.Many2one(
        'res.currency', string="Devise", company_dependent=True, default='base.DZD',
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    montant = fields.Float(string="Montant de l`autorisation", store=True, required=True)
    condition_objet = fields.Text(string="Objet et Conditions", store=True)
    date_create = fields.Datetime(string='Date de création', required=True, index=True, copy=False,
                                     default=fields.Datetime.now,
                                     help="Indicates the date the autorisation was created.",
                                     readonly=True)
    validite = fields.Date("Validité de la ligne", tracking=True, required=True)
    date_limit = fields.Date("Date limite", tracking=True)
    validite_due = fields.Date("Vérification de la date", tracking=True,default=fields.Datetime.now)
    condition = fields.Char(string='Condition non bloquante a réaliser', tracking=True)
    rappel = fields.Date("Date de rappel de renouvellement", tracking=True, store=True)
    user_id = fields.Many2one(
        'res.users', string='Order representative', index=True, tracking=True, readonly=True,
        default=lambda self: self.env.user, check_company=True)
    autorisation_global = fields.Many2one('credit.autorisation_global', ondelete='cascade', string='Autorisation global')
    financement_hauteur = fields.Float(string='Financement à hauteur de %')
    delai_mobilisation = fields.Integer(string='Délai de mobilisation')
    is_decouvert = fields.Boolean(compute='_compute_decouvert',)
    type_id = fields.Integer(string='type', compute='compute_type', store=True)
    state = fields.Selection([('draft', 'Brouillon'),
                              ('confirmed', 'Confirmé')], string='Etat', default='draft')

    @api.depends('type_ids')
    def compute_type(self):
        for rec in self:
            if rec.type_ids:
                asf = rec.type_ids.filtered(lambda l: l.id in [2, 3])
                if asf:
                    rec.type_id = 2

            else:
                rec.type_id = 0

    @api.depends('type_ids', 'montant')
    def _compute_display(self):
        for rec in self:
            print('_compute_disp executed')
            display_name = ''
            if rec.type_ids and rec.montant:
                for type in rec.type_ids:
                    print(type.name)
                    if type == rec.type_ids[0]:
                        display_name = type.titre
                    else:
                        display_name = display_name + ' / ' + type.titre
                    print(display_name)
                display_name = display_name + ' ( ' + str(rec.montant) + ' DA)'

            rec.display_name = display_name

    @api.depends('type_ids', 'montant')
    def _compute_decouvert(self):
        print('_compute_decouvert executed')
        for rec in self:
            '''if rec.type_ids and rec.montant:
                if 49 in rec.type_ids.ids and rec.montant >= 0:
                    raise UserError(_('Vous devriez saisir une valeur négatif pour le montant de l\'autorisation'))'''
            rec.is_decouvert = False

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

    def action_Disponible(self):
        for record in self:
            if record.type.id in [1, 49] and record.montant >= 0:
                raise UserError(_('Vous devriez saisir une valeur négatif pour le montant de l\'autorisation'))
            q = record.env['credit.disponible'].search([('ligne_autorisation', '=', record.id)])
            print(q)
            print(record.banque)
            val = {
                'montant_disponible': record.montant,
                'ligne_autorisation': record.id,
                'banque': record.autorisation_global.banque.id,
                'type_ids': record.type_ids.ids,
            }
            if not q:
                record.env['credit.disponible'].create(val)
            record.state = 'confirmed'


class Autorisation_global(models.Model):
    _name = 'credit.autorisation_global'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Ensemble des autorisations des lignes de crédit bancaire"

    name = fields.Char(string='Ensemble d`autorisations', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    banque = fields.Many2one(
        'credit.banque', string='Banque', index=True, tracking=True, required=True)
    ligne_autorisation = fields.One2many('credit.autorisation', 'autorisation_global', string="ligne d`autorisation")
    taux = fields.Float(string='Taux')
    file_ticket = fields.Binary(string='Ticket d`Autorisation')
    file_name = fields.Char(string='File name')
    state = fields.Selection([('draft', 'Brouillon'),
                              ('confirmed', 'Confirmé')], string='Etat')

    @api.model
    def create(self, vals):
        print(vals['banque'])
        exist = self.env['credit.autorisation_global'].search([('banque', '=', vals['banque'])])
        if exist:
            raise UserError('Cette banque existe deja dans la liste des autorisations')
        else:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('credit.autorisation_global') or _('New')
        result = super(Autorisation_global, self).create(vals)
        return result

    @api.model
    def write(self, vals):
        if 'banque' in vals:
            exist = self.env['credit.autorisation_global'].search([('banque', '=', vals['banque'])])
            if exist:
                raise UserError('Cette banque existe deja dans la liste des autorisations')
        result = super(Autorisation_global, self).write(vals)
        return result

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
                    'type_ids': aut.type_ids.ids,
                }
                if not q:
                    aut.env['credit.disponible'].create(val)
                    aut.state = 'confirmed'
                else:
                    q.write({'montant_disponible': aut.montant,
                             'type_ids': aut.type_ids.ids})
                    aut.state = 'confirmed'
            record.state = 'confirmed'
