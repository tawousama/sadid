from odoo import api, fields, models, _


class Type_credit(models.Model):
    _name = 'credit.type'
    _inherit = ["mail.thread",'mail.activity.mixin']
    _description = "types de ligne de crédit"

    name = fields.Char(string='Nom', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    titre = fields.Char(string='Types de ligne de crédit', required=True)
    note = fields.Text(string='Description', tracking=True)

    user_id = fields.Many2one(
        'res.users', string='Order representative', index=True, tracking=True, readonly=True,
        default=lambda self: self.env.user, check_company=True)

    has_autorisation = fields.Boolean(string='A une autorisation', compute='compute_autorisation',store=True)
    autorisation_ids = fields.One2many('credit.autorisation', 'type')

    has_deblocage = fields.Boolean(string='A une deblocage', compute='compute_deblocage', store=True)
    deblocage_ids = fields.One2many('credit.operation.deb', 'type')

    @api.depends('deblocage_ids')
    def compute_deblocage(self):
        for rec in self:
            print('computed')
            has_deb = self.env['credit.operation.deb'].search([('type', '=', rec.id)])
            if not has_deb:
                rec.has_deblocage = False
            else:
                rec.has_deblocage = True

    @api.depends('autorisation_ids')
    def compute_autorisation(self):
        for rec in self:
            has_autor = self.env['credit.autorisation'].search([('type', '=', rec.id)])
            if not has_autor:
                rec.has_autorisation = False
            else:
                rec.has_autorisation = True

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.type') or _('New')

        result = super(Type_credit, self).create(vals)
        return result
