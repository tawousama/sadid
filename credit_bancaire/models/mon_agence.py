from odoo import api, fields, models, _
import requests
import time
from bs4 import BeautifulSoup


class Mon_agence(models.Model):
    _name = 'credit.mon.agence'
    _inherit = ["mail.thread",'mail.activity.mixin']
    _description = "MON AGENCE"

    name = fields.Char(string='Nom de l`agence',required=True,store=True)
    code = fields.Char(string='Code de l`agence',required=True,store=True)
    adresse = fields.Char(string='Adresse de l`agence',required=True,store=True)
    num_compte = fields.Integer(string='Numéro de compte', required=True)
    contacts = fields.One2many('credit.contact','agence',string='Contacts',store=True,index=True)
    banque = fields.Many2one('credit.banque', string='Banque')

    '''@api.model
    def create(self, vals):
        agence = self.env['credit.mon.agence'].search([])
        print(len(agence))
        if len(agence) < 1:
            result = super(Mon_agence, self).create(vals)
            return result
        else:
                raise ValidationError(_("Une seule agence "))'''


class Contact(models.Model):
    _name = 'credit.contact'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "CONTACTS"

    nom = fields.Char(string='Nom', required=True, store=True)
    prenom = fields.Char(string='Prenom', required=True, store=True)
    poste = fields.Char(string='Poste', required=True, store=True)
    telephone = fields.Integer(string='Telephone', required=True)
    mail = fields.Char(string='Mail', required=True)
    agence = fields.Many2one('credit.mon.agence', string='Agence')
    linkedin_accounts = fields.One2many('credit.linkedin', 'contact', string='Comptes linkedin')

    def action_linkedin(self):
        for rec in self:
            dict = []
            url = "https://www.google.com/search?q="+rec.nom+"+"+rec.prenom+"+"+rec.poste+"+linkedin"
            response = requests.get(url,timeout=3)
            soup = BeautifulSoup(response.text, 'html.parser')
            time.sleep(5)
            result = soup.findAll('div', {'class': 'Gx5Zad fP1Qef xpd EtOod pkphOe'})
            for r in result:
                link = r.find('a').get('href')
                if "linkedin.com/in/" and  not "trk%3" in link:
                    title = r.find('h3')
                    str = "/url?q="
                    new_link = link.split(str)
                    pos = new_link[1].find('&sa')
                    print(pos)
                    link_1 = new_link[1][0:pos]
                    dict.append((title.text, link_1))
            for rec in self:
                linkedin = rec.env['credit.linkedin'].search([('contact', '=', rec.id)])
                if linkedin:
                    for l in linkedin:
                        l.unlink()
                for i, j in dict:
                    linked = rec.env['credit.linkedin'].create({
                        'title': i,
                        'link': j,
                        'contact': rec.id
                    })
            print(len(dict))
    def action_cancel_linkedin(self):
        for rec in self:
            linkedin = rec.env['credit.linkedin'].search([('contact', '=', rec.id)])
            for l in linkedin:
                l.unlink()


class Linkedin_Account(models.Model):
    _name = 'credit.linkedin'
    _description = "COMPTES LINKEDIN"

    link = fields.Char(string='Lien du compte')
    title = fields.Char(string='Compte linkedin')
    contact = fields.Many2one('credit.contact',string='Contact')

