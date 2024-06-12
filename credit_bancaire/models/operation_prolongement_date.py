from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Gestion_operation_pd(models.Model):
    _name = 'credit.operation.pd'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Opérations bancaire"

    name = fields.Char(string='Opération', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    echeance_date_old = fields.Date("Date d'échéance initiale", compute='_compute_date_old',readonly=True,store=True)
    echeance_date_new = fields.Date("Nouvelle date d'échéance", store=True)
    note = fields.Text(string='Description', tracking=True)
    user_id = fields.Many2one(
        'res.users', string='Order representative', index=True, tracking=True, readonly=True,
        default=lambda self: self.env.user, check_company=True)
    ref_opr_deb = fields.Many2one('credit.operation.deb', string='Opération de déblocage', ondelete='cascade',
                                  domain="[('banque_id.id', '=', banque),('type.id', '=', type),('state', '=', 'confirmed')]", store=True )
    banque = fields.Many2one(
        'credit.banque', string='Banque', index=True, tracking=True, required=True, domain="[('has_deblocage', '=', True)]")
    type = fields.Many2one(
        'credit.type', string='Ligne de crédit', index=True, tracking=True, domain="[('has_deblocage', '=', True)]")
    type_ids = fields.Many2many(
        'credit.type', string='Ligne de crédit', index=True, tracking=True, related="ligne_autorisation.type_ids")

    ligne_autorisation = fields.Many2one('credit.autorisation', string='Autorisation',
                                        domain="[('banque.id', '=', banque),('type.id', '=', type),('state', '=', 'confirmed')]",
                                         ondelete='cascade')
    state = fields.Selection([
        ('verification', 'Verification'),
        ('confirm', 'Confirmed'),
    ], string='Status', required=True, default='verification')
    date_create = fields.Datetime(string='Date de création', required=True, index=True, copy=False,
                                  default=fields.Datetime.now,
                                  help="Indicates the date the operation pd was created.",
                                  readonly=True)
    date_origin = fields.Date("confirmation d`échéance", readonly=True, compute='_compute_date_confirm',store=True)
    file_accord = fields.Binary(string='Accord de la banque')
    file_name1 = fields.Char(string='File name')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.operation.pd') or _('New')
        result = super(Gestion_operation_pd, self).create(vals)
        return result
    ''''
    def write(self, vals):
        # your code
        for rec in self:
            rec.ligne_autorisation.validite_old = rec.ligne_autorisation.validite
        result = super(Gestion_operation_pd, self).create(vals)
        return result
    '''
    def action_validation(self):
        for rec in self:
            if rec.echeance_date_new < rec.echeance_date_old:
                raise ValidationError(_("The new date is less than the old date !!! "))
            else:
                print(rec.echeance_date_new)
                rec.ref_opr_deb.echeance_date = rec.echeance_date_new
                ech = rec.env['credit.echeance'].search([('ref_opr_deb','=',rec.ref_opr_deb.id),('echeance','=',None)])
                ech.echeance_date = rec.echeance_date_new
                pay = rec.env['credit.operation.p'].search(
                    [('ref_opr_deb', '=', rec.ref_opr_deb.id), ('echeance', '=', None)])
                print(pay.montant_a_rembourser)
                print(pay.date_echeance)
                pay.date_echeance = rec.echeance_date_new
                '''rec.ligne_autorisation.validite_old = rec.ligne_autorisation.validite
                rec.ligne_autorisation.validite = rec.echeance_date_new
                rec.echeance_date_old = rec.ligne_autorisation.validite_old'''
                self.state = 'confirm'
                print('origin', rec.date_origin)

    @api.depends('ref_opr_deb')
    def _compute_date_old(self):
        for rec in self:
            print(self)
            print(rec)
            print(rec.echeance_date_old)
            if not rec.echeance_date_old:
                rec.echeance_date_old = rec.ref_opr_deb.echeance_date
                print('rec.echeance_date_old2 ', rec.echeance_date_old)
                print(rec.date_origin)

    @api.depends('ref_opr_deb')
    def _compute_date_confirm(self):
        print(self)
        self.date_origin = self.ref_opr_deb.echeance_date
        print('rec.echeance_date_old1 ', self.date_origin)

    def unlink(self):
        for rec in self:
            prol = rec.env['credit.operation.pd'].search([('ref_opr_deb', '=', rec.id)])
            if len(prol) == 1:
                rec.ref_opr_deb.echeance_date = rec.echeance_date_old
                ech = rec.env['credit.echeance'].search(
                    [('ref_opr_deb', '=', rec.ref_opr_deb.id), ('echeance', '=', None)])
                ech.echeance_date = rec.echeance_date_old
                pay = rec.env['credit.operation.p'].search(
                    [('ref_opr_deb', '=', rec.ref_opr_deb.id), ('echeance', '=', None)])
                pay.date_echeance = rec.echeance_date_old
            else :
                newest = rec.echeance_date_old
                for p in prol:
                    if p.echeance_date_new > newest:
                        newest = p.echeance_date_new
                rec.ref_opr_deb.echeance_date = newest
                ech = rec.env['credit.echeance'].search(
                    [('ref_opr_deb', '=', rec.ref_opr_deb.id), ('echeance', '=', None)])
                ech.echeance_date = newest
                pay = rec.env['credit.operation.p'].search(
                    [('ref_opr_deb', '=', rec.ref_opr_deb.id), ('echeance', '=', None)])
                pay.date_echeance = newest
        return super(Gestion_operation_pd, self).unlink()