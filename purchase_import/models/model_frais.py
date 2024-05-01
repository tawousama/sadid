# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from odoo.exceptions import  UserError


class ImportFolderFraisModel(models.Model):
    _name= "purchase.import.model.frais"
    _rec_name = "reference"
    
    reference = fields.Char(string='Référence')
    date = fields.Date(string='Date')
    active = fields.Boolean(string='Active?',default=True)
    product_lines = fields.One2many(
        'purchase.import.model.frais.products', 'frais_model_id',
        string='Lines')


class ImportFolderPurchasesProducts(models.Model):
    _name= "purchase.import.model.frais.products"
    _rec_name = "product_id"
    
    frais_model_id = fields.Many2one("purchase.import.model.frais",string='Modèle')
    amount = fields.Float(string='Montant')
    product_id = fields.Many2one("product.product",string='Produit',required=True)