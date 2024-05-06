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
