import datetime

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
                    'message': _('Compte credité avec succés')})
        if self.env.context.get('payment'):
            payment = self.env['credit.operation.p'].browse(self.env.context.get('payment'))
            print(payment)
            self.env['account.payment'].create({'payment_type':'outbound',
                                                'amount': payment.montant_echeance,
                                                'date': datetime.datetime.today(),
                                                'partner_type': 'supplier',
                                                'ref': payment.name})
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                    'type': 'success',
                    'sticky': False,
                    'message': _('Compte debité avec succés'),

         })
    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class BudgetRequest(models.Model):
    _name = 'budget.request'

    name = fields.Char()
    start_date = fields.Date(string='Date debut')
    end_date = fields.Date(string='Date fin')
    amount = fields.Float(string='Montant')
    description = fields.Text(string='Commentaire')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    state = fields.Selection([('send', 'Envoyé'),
                              ('deleted', 'Annulé')], default='send',
                              string='Etat')
