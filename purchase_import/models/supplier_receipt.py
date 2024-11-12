from odoo import models, fields

class SupplierReceipt(models.Model):
    _name = 'supplier.receipt'
    _description = 'Dossiers Attestation de non-transfert'

    supplier_name = fields.Many2one("res.partner", string='Fournisseur',
                                 domain="[('partner_type', '=', 'supplier'),('supplier_type', '=', 'etranger')]")
    reception_validation_date = fields.Date(string='Date réception fiche validation')
    attachment = fields.Binary(string='Attachement')
    order_number = fields.Char(string='Numéro de commande')
    currency_id = fields.Many2one('res.currency', string='Devise')
    country_of_origin = fields.Char(string='Pays d\'origine')
    dhl_reception_date = fields.Date(string='Date réception pli DHL')
    non_transfer_certificate_establishment_date = fields.Date(string='Date établissement attestation de non-transfert')
    non_transfer_certificate_retrieval_date = fields.Date(string='Date récup attestation non-transfert')
    shipping_date = fields.Date(string='Date d\'embarquement')
    goods_arrival_date = fields.Date(string='Date d\'arrivée de marchandises')
