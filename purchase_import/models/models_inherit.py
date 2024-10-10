# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    import_folder = fields.Many2one("purchase.import.folder", string='Dossier')
    is_import = fields.Boolean(string='Est importation?')
    conditions = fields.Text(string='Conditions')


class AccountInvoice(models.Model):
    _inherit = "account.move"

    import_folder = fields.Many2one("purchase.import.folder", string='Dossier')
    is_import = fields.Boolean(string='Est importation?')


class StockPicking(models.Model):
    _inherit = "stock.picking"

    import_folder = fields.Many2one("purchase.import.folder", string='Dossier')
    is_import = fields.Boolean(string='Est importation?')


class Tarif(models.Model):
    _name = "import.tarif"

    name = fields.Char(string='Article')
    tarif = fields.Char(string='Tarif douane')


class Deblocage(models.Model):
    _inherit = "credit.operation.deb"

    folder_id = fields.Many2one('purchase.import.folder', string='Dossier')
    lc_id = fields.Many2one('purchase.import.folder', string='LC Ouvertes')
    remdoc = fields.Char(string='REMDOC')
    dom_ref = fields.Many2one('import.dom', string='Reference dossier Dom.')
    def action_create_file(self):
        for rec in self:
            if rec.type_ligne == '1':
                if rec.type == self.env.ref('credit_bancaire.04'):
                    view_id = self.env.ref('purchase_import.view_purchase_import_folder_form').id
                    return {
                        'type': 'ir.actions.act_window',
                        'name': _('Créer le dossier'),
                        'res_model': 'purchase.import.folder',
                        'view_mode': 'form',
                        'views': [[view_id, 'form']],
                        'context': {'default_deblocage_id': rec.id,
                                    'default_partner_id': rec.partner_id.id,
                                    'default_bank_id': rec.banque_id.id,
                                    'default_montant_debloque_spot_prefin': rec.montant_debloque,
                                    'default_date_ouverture_lc': rec.deblocage_date,
                                    'deblocage': rec.id}
                    }

    def open_folder(self):
        for rec in self:
            if rec.type_ligne == '1':
                if rec.type == self.env.ref('credit_bancaire.04'):
                    print('LC A VUE')
                    view_id = self.env.ref('purchase_import.view_purchase_import_folder_form').id
                    dossier = self.env['purchase.import.folder'].search([('deblocage_id', '=', rec.id)])
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'purchase.import.folder',
                        'res_id': dossier.id,
                        'view_mode': 'form',
                        'views': [[view_id, 'form']],
                    }


class Payment(models.Model):
    _inherit = 'account.payment'

    dossier = fields.Many2one('purchase.import.folder', string='Référence Dom.',
                              domain="[('partner_id', '=', partner_id)]")
    lc_id = fields.Many2one('purchase.import.folder', string='Référence LC',
                            domain="[('journal_id', '=', journal_id)]")

    @api.model
    def create(self, vals):
        res = super(Payment, self).create(vals)
        if 'dossier_id' in self.env.context:
            dossier = self.env['purchase.import.folder'].browse(self.env.context.get('dossier_id'))
            if dossier:
                dossier.payment_id = res.id
        return res


class RefDom(models.Model):
    _name = "import.dom"

    name = fields.Char(string='Reference')
