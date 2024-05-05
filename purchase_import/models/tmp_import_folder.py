# -*- coding: utf-8 -*-

from odoo import api,fields,models,_
from odoo.exceptions import  UserError


class ImportFolder(models.Model):
    _name= "purchase.import.folder"
    _rec_name = "reference"
    
    reference = fields.Char(string='Référence')
    note = fields.Text(string='Note')
    partner_id = fields.Many2one("res.partner",string='Fournisseur')
    property_purchase_currency_id = fields.Many2one(
        'res.currency', string="Devise", company_dependent=True,
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    #Champs importations
    port_embarquement = fields.Char(string="Port d'embarquement")
    navire = fields.Char(string='Navire')
    compagnieie_maritime = fields.Char(string='Compagnie maritime')
    n_bl = fields.Char(string='N° B/L')
    etd = fields.Char(string='ETD')
    eta = fields.Char(string='ETA')
    tracking_doc = fields.Char(string='Tracking Doc')
    #Champs remise documentaire
    ouverture_dossier = fields.Char(string='Ouverture dossier')
    payment_modality = fields.Many2one("purchase.import.payment.modality",string='Modalité de paiement.xml')
    #Commun
    acceptation_dossier = fields.Char(string='Ouverture dossier')
    cheque_bank = fields.Char(string='Chèque de banque')
    taux_change = fields.Char(string='règlement (Taux de change)')
    commission_reglement = fields.Char(string='commission règlement')
    swift_reglement = fields.Char(string='Swift règlement')
    assurance_couverture_par = fields.Char(string='Assurance couverture par')
    type_livraison = fields.Many2one("purchase.import.livraison.type",string='Type de livraison')
    moyen_livraison = fields.Many2one("purchase.import.livraison.moyen",string='Moyen de livraison')
    #Champs LC
    ouverture_lc = fields.Char(string='ouverture LC')
    swift_ouverture = fields.Char(string='Swift ouverture')
    modification = fields.Char(string='Modification')
    #2nd LC
    credit_forme = fields.Many2one("purchase.import.credit.forme",string='Forme du crédit')
    date_validite = fields.Char(string='Date de validité')
    lieu_validite = fields.Char(string='Lieu de validité')
    spec_montant = fields.Char(string='Spécialisation du montant')
    condition_livraison = fields.Text(string='Condition de livraison')
    start_pres_documents = fields.Date(string='Début présentation des documents')
    end_pres_documents = fields.Date(string='Fin présentation des documents')
    date_limit_embarequement = fields.Date(string="Date limite d'embarequement")
    date = fields.Date(string='Date')
    date_embarequement = fields.Date(string="Date d'embarequement")
    payment_mode = fields.Selection([
        ('L.C', 'L.C'),
        ('remise_documentaire_vue', 'Remise documentaire à vue'),
        ('remise_documentaire_echeance', 'Remise documentaire à écheance'),
        ('transfert_libre', 'transfert libre'),
        ('sans_paiement', 'Sans paiement.xml'),
        ], 
        string="Mode de paiement.xml",
        copy=False)
        
    # default="draft",
    state_rd = [
        ('draft', 'Brouillon'),
        ('confirmation', 'Confirmation'),
        ('production', 'En cours de production'),
        ('expedition', 'Expédition marchandise'),
        ('assurence', 'Assurance transport Maritime'),
        ('Récéption documants (Banque)', 'Récéption documants (Banque)'),
        ('Pré-domiciliation', 'Pré-domiciliation'),
        ('Domiciliation', 'Domiciliation'),
        ('Retrait documents (banque)', 'Retrait documents (banque)'),
        ('Dépôt transitaire/Documents', 'Dépôt transitaire/Documents'),
        ('Arrivée marchandise', 'Arrivée marchandise'),
        ('Paiement fournisseur', 'Paiement fournisseur'),
        ('Dédouanement en cours', 'Dédouanement en cours'),
        ('Chèque de douane', 'Chèque de douane'),
        ('Réception marchandise', 'Réception marchandise'),
        ('Accusé de confirmation', 'Accusé de confirmation'),
        ('Récéption dossier Transit', 'Récéption dossier Transit'),
        ('Retrait dossier comptable', 'Retrait dossier comptable'),
        ('Accusé de confirmation', 'Accusé de confirmation'),
        ('Terminée', 'Terminée')
        # ('canceld', 'Annulé'),
        # ('done', 'Validé')
        ]

    state_lc = [
        ('draft', 'Brouillon'),
        ('confirmation', 'Confirmation'),
        ('Pré-domiciliation', 'Pré-domiciliation'),
        ('ouverture lc', 'Ouverture LC'),
        ('production', 'En cours de production'),
        ('expedition', 'Expédition marchandise'),
        ('assurence', 'Assurance transport Maritime'),
        ('Récéption documants (Banque)', 'Récéption documants (Banque)'),
        ('Paiement fournisseur', 'Paiement fournisseur'),
        ('Retrait documents (banque)', 'Retrait documents (banque)'),
        ('Dépôt transitaire/Documents', 'Dépôt transitaire/Documents'),
        ('Arrivée marchandise', 'Arrivée marchandise'), 
        ('Dédouanement en cours', 'Dédouanement en cours'),
        ('Chèque de douane', 'Chèque de douane'),
        ('Réception marchandise', 'Réception marchandise'),
        ('Accusé de confirmation', 'Accusé de confirmation'),
        ('Récéption dossier Transit', 'Récéption dossier Transit'),
        ('Retrait dossier comptable', 'Retrait dossier comptable'),
        ('Terminée', 'Terminée')
        ]
    
    state_tl = [
        ('draft', 'Brouillon'),
        ('confirmation', 'Confirmation'),
        ('production', 'En cours de production'),
        ('expedition', 'Expédition marchandise'),
        ('Récéption documants', 'Récéption documants'), 
        ('Retrait documents (banque)', 'Retrait documents (banque)'),
        ('Dépôt transitaire/Documents', 'Dépôt transitaire/Documents'),
        ('Arrivée marchandise', 'Arrivée marchandise'),
        ('Dédouanement en cours', 'Dédouanement en cours'),
        ('Chèque de douane', 'Chèque de douane'),
        ('Réception marchandise', 'Réception marchandise'),
        ('Accusé de confirmation', 'Accusé de confirmation'),
        ('Récéption dossier Transit', 'Récéption dossier Transit'),
        ('Paiement fournisseur', 'Paiement fournisseur'),
        ('Retrait dossier comptable', 'Retrait dossier comptable'),
        ('Terminée', 'Terminée')
        ]

    state_sp = [
        ('draft', 'Brouillon'),
        ('confirmation', 'Confirmation'),
        ('production', 'En cours de production'),
        ('expedition', 'Expédition marchandise'),
        ('Récéption documants', 'Récéption documants'), 
        ('Dépôt transitaire/Documents', 'Dépôt transitaire/Documents'),
        ('Arrivée marchandise', 'Arrivée marchandise'),
        ('Dédouanement en cours', 'Dédouanement en cours'),
        ('Chèque de douane', 'Chèque de douane'),
        ('Réception marchandise', 'Réception marchandise'),
        ('Accusé de confirmation', 'Accusé de confirmation'),
        ('Récéption dossier Transit', 'Récéption dossier Transit'),
        ('Retrait dossier comptable', 'Retrait dossier comptable'),
        ('Terminée', 'Terminée')
        ]

    liste_state = [
        ('draft', 'Brouillon')
    ]
    
    state = fields.Selection(selection=liste_state, string='État', required=True, readonly=True, copy=False, tracking=True,default='draft')

    @api.onchange('payment_mode')	
    def _session_payment_mode(self):
        for record in self:
            if record.payment_mode == 'L.C':
                for m in record.state_lc:
                    record.liste_state = []
                    record.liste_state.append(m)
            else:
                for m in record.state_lc:
                    record.liste_state = []
                    record.liste_state.append(m)
                # return record.liste_state
                # raise UserError(record.liste_state)
                # record.liste_state = record.state_lc
                    # raise UserError(record.liste_state)
                    # record.liste_state = record.state_lc
                    # raise UserError(record.state)
                    # record.liste_state.append(m)
                    # raise UserError(record.liste_state)
                    # record.state = record.state_lc

   
    
    # state = fields.Selection(liste_state,
    #     string="État",
    #     default="draft",
    #     copy=False)
        
    # @api.depends('payment_mode')
    # def payment_mode_state(self):
    #     for record in self:
    #         if record.payment_mode == 'L.C':
    #             # for m in record.state_lc:
    #             raise UserError(record.state)
    #                 # record.liste_state.append(m)
    #                 # raise UserError(record.state)
    #                 # record.state = record.state_lc
    #         elif record.payment_mode == 'remise_documentaire_vue' or record.payment_mode == 'remise_documentaire_echeance':
    #             for m in record.state_rd:
    #                 record.liste_state.append(m)
    #                 # raise UserError(record.liste_state)
    #         elif record.payment_mode == 'transfert_libre':
    #             for m in record.state_tl:
    #                 record.liste_state.append(m)
    #         elif record.payment_mode == 'sans_paiement':
    #             for m in record.state_sp:
    #                 record.liste_state.append(m)
    #         else:
    #             for m in record.state_lc:
    #                 record.liste_state.append(m)
    
     #update 

    # def _get_status_list(self):
    #     if self.payment_mode == 'L.C':
    #         raise UserError(self.payment_mode)
    #     else: 
    #         return [(1, 'option1')]

    # state = fields.Selection(selection=liste, string='État', required=True, readonly=True, copy=False, tracking=True,default='draft')
    
    # Update
    
    # state= fields.Selection(selection=lambda self: self.dynamic_selection())

    def _get_status_list(self):
        self._call_dynamic_selection()

    @api.onchange('payment_mode')	
    def _call_dynamic_selection(self):
        if self.payment_mode == 'L.C':
            return [('yes', 'Yes'), ('no', 'No')]
        elif self.payment_mode == 'remise_documentaire_vue':
            return [('yes', 'Yes'), ('no', 'No')]
        elif self.payment_mode == 'remise_documentaire_echeance':
           return [('yes', 'Yes'), ('no', 'No')]
        elif self.payment_mode == 'transfert_libre':
           return [('yes', 'Yes'), ('no', 'No')]
        elif self.payment_mode == 'sans_paiement':
            return [('yes', 'Yes'), ('no', 'No')]
        else: 
            return self.liste
    
    state = fields.Selection(selection=_get_status_list, string='Status')

        # raise UserError(dict(self._fields['payment_mode'].selection).get(self.payment_mode))
        # print dict(self._fields['type'].selection).get(self.type)
        # raise UserError(self.payment_mode)
        # if self.payment_mode == 'L.C':
        #     select = [('yes', 'Yes'), ('no', 'No')]
        #     return select
        # else:
           
    # @api.one
    # @api.onchange('payment_mode')	
    # def _payment_mode(self):
        # if str(dict(self._fields['payment_mode'].selection).get(self.payment_mode)) == 'L.C':
        #     self._fields['payment_mode'].selection = [('yes', 'Yes'), ('no', 'No')]
        # else:
        #     self._fields['payment_mode'].selection = [('yes', 'Yes')]

    # Fin update
    purchase_ids = fields.One2many(
        'purchase.import.folder.purchases', 'folder_id',
        string='Lines')
    invoice_ids = fields.One2many(
        'purchase.import.folder.invoices', 'folder_id',
        string='Lines')
    detail = fields.Text(string="Détail")

    #2nd LC document exigés 
    facture_commerciale = fields.Boolean(string="Facture commerciale", default=False)
    jeu_complet_connaissement = fields.Boolean(string="Jeu complet de connaissement", default=False)
    lettre_transport = fields.Boolean(string="Lettre de transport", default=False)
    certificat_origine = fields.Boolean(string="certificat d'origine", default=False)
    certificat_analyse = fields.Boolean(string="certificat d'analyse", default=False)
    certificat_sanitaire = fields.Boolean(string="certificat sanitaire", default=False)
    certificat_confirmite = fields.Boolean(string="certificat de confirmité", default=False)
    certificat_controle_qualite = fields.Boolean(string="certificat contrôle de qualité", default=False)
    certificat_non_radioactivite = fields.Boolean(string="certificat de non radioactivité", default=False)
    liste_colisage = fields.Boolean(string="Liste de colisage", default=False)
    note_poids = fields.Boolean(string="Note de poids", default=False)
    autre_document_transport = fields.Boolean(string="Autre document de transport", default=False)
    autres = fields.Boolean(string="Autres", default=False)
    
    proformat = fields.Char(string='N° Proformat')
    total = fields.Float(string='Montant', compute='_get_montant',default=0)

    def _get_montant(self):
        for folder in self :
            for line in folder.purchase_ids:
                folder.total = folder.total + line.amount_total
                #raise UserError(folder.total)
        
        
        
    
    def update_list(self):
        lines =[]
        self.update({'purchase_ids': None})
        self.update({'invoice_ids': None})
        order_list = self.env['purchase.order'].search( [('import_folder','=',self.id)])
        for val in order_list:
            line_item = {
                          'purchase_id': val['id'],
                        }
            lines.append([0,0,line_item])
        self.update({'purchase_ids': lines})


    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('purchase.import.folder') or 'New'    
        result = super(ImportFolder, self).create(vals)
        return result

    def action_done(self):
        self.state = "done"

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft'):
                raise UserError(_('Vous ne pouvez pas supprimer un élément non brouillon'))
        return super(Tourne, self).unlink()



class ImportFolderPurchases(models.Model):
    _name= "purchase.import.folder.purchases"
    
    purchase_id = fields.Many2one("purchase.order",string='Achat')
    partner_id = fields.Many2one(related='purchase_id.partner_id',string='Partenaire')
    date_order = fields.Datetime(related='purchase_id.date_order',string='Date')
    state = fields.Selection(
        related='purchase_id.state')
    conditions = fields.Text(related='purchase_id.conditions')
    currency_id = fields.Many2one(related='purchase_id.currency_id')
    amount_total = fields.Monetary(
        related='purchase_id.amount_total')
    folder_id = fields.Many2one(
        'purchase.import.folder',
        string='Lines', readonly=True)


class ImportFolderInvoices(models.Model):
    _name= "purchase.import.folder.invoices"
    
    invoice_id = fields.Many2one("account.move",string='Facture', domain=[('move_type', '=', 'in_invoice')] )
    partner_id = fields.Many2one(related='invoice_id.partner_id',string='Partenaire')
    date_invoice = fields.Date(related='invoice_id.date',string='Date')
    state = fields.Selection(
        related='invoice_id.state')
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    amount_total = fields.Monetary(
        related='invoice_id.amount_total')
    folder_id = fields.Many2one(
        'purchase.import.folder',
        string='Lines', readonly=True)



class TypeLivraison(models.Model):
    _name= "purchase.import.livraison.type"
    _rec_name="desc"
    
    name = fields.Char(string='Nom')
    desc = fields.Char(string='Déscription')



class MoyenLivraison(models.Model):
    _name= "purchase.import.livraison.moyen"
    _rec_name="desc"
    
    name = fields.Char(string='Nom')
    desc = fields.Char(string='Déscription')


class CreditForm(models.Model):
    _name= "purchase.import.credit.forme"
    _rec_name="desc"
    
    name = fields.Char(string='Nom')
    desc = fields.Char(string='Déscription')

class PaymentModalite(models.Model):
    _name= "purchase.import.payment.modality"
    _rec_name="desc"
    
    name = fields.Char(string='Nom')
    desc = fields.Char(string='Déscription')