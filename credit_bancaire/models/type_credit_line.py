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


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.type') or _('New')

        result = super(Type_credit, self).create(vals)
        return result
