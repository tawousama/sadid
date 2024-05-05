from odoo import api, fields, models, _

class Wizard(models.TransientModel):
    _name = 'wizard.credit.deblocage'

    def send(self):
        print(self.env.context.get('deblocage'))
        if self.env.context.get('deblocage'):
            deblocage = self.env['credit.operation.deb'].browse(self.env.context.get('deblocage'))
            print(deblocage)
            self.env['account.payment'].create({'payment_type':'inbound',
                                                'amount': deblocage.montant_debloque,
                                                'date': deblocage.deblocage_date,
                                                'ref': deblocage.name})
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                    'type': 'success',
                    'sticky': False,
                    'message': _('Compte credité avec succés'),

         })
    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class Dossier(models.Model):
    _inherit = 'purchase.import.folder'

    deblocage_id = fields.Many2one('credit.operation.deb', string='Deblocage')
    computed_field = fields.Boolean(string='Compute', store=True, compute='compute_deblocage')

    @api.model
    def create(self, vals):
        res = super(Dossier, self).create(vals)
        if self.env.context.get('deblocage'):
            res.deblocage_id = self.env['credit.operation.deb'].browse(self.env.context.get('deblocage'))
            res.deblocage_id.folder_id = res.id
        return res
