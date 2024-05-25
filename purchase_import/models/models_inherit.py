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


class Deblocage(models.Model):
    _inherit = "credit.operation.deb"

    folder_id = fields.Many2one('purchase.import.folder', string='Dossier')
    lc_id = fields.Many2one('purchase.import.folder', string='LC Ouvertes')
    remdoc = fields.Char(string='REMDOC')


    def action_create_file(self):
        for rec in self:
            if rec.type_ligne == '1':
                if rec.type == self.env.ref('credit_bancaire.04'):
                    print('LC A VUE')
                    view_id = self.env.ref('purchase_import.view_purchase_import_folder_form').id
                    return {
                        'type': 'ir.actions.act_window',
                        'name': _('Créer le dossier'),
                        'res_model': 'purchase.import.folder',
                        'view_mode': 'form',
                        'views': [[view_id, 'form']],
                        'context': {'default_deblocage_id': rec.id,'deblocage': rec.id}
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
