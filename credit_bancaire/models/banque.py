from odoo import api, fields, models, _
import requests
import time
from bs4 import BeautifulSoup
from odoo.exceptions import ValidationError
import json

class banque(models.Model):
    _name = 'credit.banque'
    _inherit = ["mail.thread",'mail.activity.mixin']
    _description = "LISTE ETABLISSEMENTS BANCAIRES"

    name = fields.Char(string='Désignation', required=True, copy=False)
    code = fields.Char(string='Code', required=True, copy=False)
    #note = fields.Text(string='Description', tracking=True)
    adresse_siege = fields.Char(string='Adresse du siège social')
    journal_id = fields.Many2one('account.journal', string='Journal')
    partner_id = fields.Many2one('res.partner', string='Client/ Fournisseur')
    web_site = fields.Char(string='Site web')
    nbr_agences = fields.Integer(string='Nombre d`agence')
    agences = fields.One2many('credit.banque.agence','banque',string='Liste des agences')
    actualitees = fields.One2many('credit.banque.actualite','banque',string='Actualitées')
    mes_agences = fields.One2many('credit.mon.agence','banque',string='Mon agence')

    has_autorisation = fields.Boolean(string='A une autorisation', compute='compute_autorisation', store=True)
    autorisation_ids = fields.One2many('credit.autorisation', 'banque')

    has_deblocage = fields.Boolean(string='A une deblocage', compute='compute_deblocage', store=True)
    deblocage_ids = fields.One2many('credit.operation.deb', 'banque_id')

    @api.depends('autorisation_ids')
    def compute_autorisation(self):
        for rec in self:
            print('computed')
            has_autor = self.env['credit.autorisation'].search([('banque', '=', rec.id)])
            if not has_autor:
                rec.has_autorisation = False
            else:
                rec.has_autorisation = True

    @api.depends('deblocage_ids')
    def compute_deblocage(self):
        for rec in self:
            print('computed')
            has_deb = self.env['credit.operation.deb'].search([('banque_id', '=', rec.id)])
            if not has_deb:
                rec.has_deblocage = False
            else:
                rec.has_deblocage = True

    def action_actualite(self):
        name = self.name
        print(name)
        name1 = name.replace(' ', '+')
        search = name1.replace("'", '%27')
        print(search)
        dictionary = []
        """headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        }
        response = requests.get(
            "https://www.google.com/search?q="+search+"&tbm=nws", headers=headers, timeout=5)
"""
        payload = {'api_key': '642f672a21547bd7e1611566', 'q': search, 'gl': 'fr'}
        response = requests.get('https://api.serpdog.io/news', params=payload)
        print(response.text)
        soup = json.loads(response.text)
        print(soup)
        if len(soup) != 0:
            for rec in self:
                actu = rec.env['credit.banque.actualite'].search([('banque', '=', rec.id)])
                for a in actu:
                    a.unlink()
                for i in soup["news_results"][:10]:
                    act = rec.env['credit.banque.actualite'].create({
                       'title': i["title"],
                        'link': i['url'],
                        'banque': rec.id
                    })


class agence(models.Model):
    _name = 'credit.banque.agence'
    _inherit = ["mail.thread",'mail.activity.mixin']
    _description = "LISTE DES AGENCES DES ETABLISSEMENTS BANCAIRES"

    agence = fields.Char(string='Agence',required=True)
    adresse = fields.Char(string='Adresse', required=True)
    banque = fields.Many2one('credit.banque',string='Banque')


class actualite(models.Model):
    _name = 'credit.banque.actualite'

    title = fields.Char(string='Titre')
    link = fields.Char(string='Le lien de l`article')
    banque = fields.Many2one('credit.banque', string='Banque')

