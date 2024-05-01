# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError





class ImportFolder(models.Model):
    _name = "purchase.import.folder"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "reference"

    reference = fields.Char(string='Référence')
    note = fields.Text(string='Note')
    proformat = fields.Char(string="Proformat")
    partner_id = fields.Many2one("res.partner", string='Fournisseur')
    transitaire_id = fields.Many2one("res.partner", string='Transitaire')
    date_usine = fields.Date(string="Date entrée usine")
    currency_id = fields.Many2one(
        'res.currency', string="Devise", company_dependent=True,
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    # Champs importations
    port_embarquement = fields.Char(string="Port d'embarquement")
    navire = fields.Char(string='Navire')
    compagnieie_maritime = fields.Char(string='Compagnie maritime')
    n_bl = fields.Char(string='N° B/L')
    etd = fields.Char(string='ETD')
    eta = fields.Char(string='ETA')
    tracking_doc = fields.Char(string='Tracking Doc')
    # Champs remise documentaire
    ouverture_dossier = fields.Char(string='Ouverture dossier')
    payment_modality = fields.Many2one("purchase.import.payment.modality", string='Modalité de paiement')
    echeance_date = fields.Date(string="Date d'échéance")
    fiance_sur = fields.Float(string="Financé sur")
    reglement_date = fields.Date(string="Date de règlement")
    echeance_amount = fields.Float(string='Montant échéance')
    # Commun
    acceptation_dossier = fields.Char(string='Ouverture dossier')
    cheque_bank = fields.Char(string='Chèque de banque DD')
    commission_reglement = fields.Char(string='commission règlement')
    swift_reglement = fields.Char(string='Swift règlement')
    assurance_couverture_par = fields.Char(string='Assurance couvert par')
    apport_society = fields.Char(string='Apport société')
    type_livraison = fields.Many2one("purchase.import.livraison.type", string='Type de livraison')
    moyen_livraison = fields.Many2one("purchase.import.livraison.moyen", string='Moyen de livraison')
    # Champs LC
    ouverture_lc = fields.Char(string='ouverture LC')
    swift_ouverture = fields.Char(string='Swift ouverture')
    modification = fields.Char(string='Modification')
    # 2nd LC
    credit_forme = fields.Many2one("purchase.import.credit.forme", string='Forme du crédit')
    model_id = fields.Many2one("purchase.import.model.frais", string='Modèle des frais')
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
        ('sans_paiement', 'Sans paiement'),
    ],
        default='L.C',
        string="Mode de paiement",
        copy=False)

    STATE_RD = [
        ('draft', 'Brouillon'),
        ('confirmation', 'Confirmation'),
        ('production', 'En cours de production'),
        ('expedition', 'Expédition marchandise'),
        ('assurence', 'Assurance transport Maritime'),
        ('reception documants', 'Récéption documants (Banque)'),
        ('Predomiciliation', 'Pré-domiciliation'),
        ('Domiciliation', 'Domiciliation'),
        ('Retrait documents', 'Retrait documents (banque)'),
        ('depot transitaire/Documents', 'Dépôt transitaire/Documents'),
        ('Arrivee marchandise', 'Arrivée marchandise'),
        ('Paiement fournisseur', 'Paiement fournisseur'),
        ('Dédouanement en cours', 'Dédouanement en cours'),
        ('Cheque de douane', 'Chèque de douane'),
        ('Reception marchandise', 'Réception marchandise'),
        ('Accuse de confirmation', 'Accusé de confirmation'),
        ('Reception dossier Transit', 'Récéption dossier Transit'),
        ('Retrait dossier comptable', 'Retrait dossier comptable'),
        ('Accuse de confirmation', 'Accusé de confirmation'),
        ('Terminee', 'Terminée')
        # ('canceld', 'Annulé'),
        # ('done', 'Validé')
    ]

    STATE_LC = [
        ('draft', 'Brouillon'),
        ('confirmation', 'Confirmation'),
        ('Predomiciliation', 'Pré-domiciliation'),
        ('ouverture lc', 'Ouverture LC'),
        ('production', 'En cours de production'),
        ('expedition', 'Expédition marchandise'),
        ('assurence', 'Assurance transport Maritime'),
        ('Reception documants (Banque)', 'Récéption documants (Banque)'),
        ('Paiement fournisseur', 'Paiement fournisseur'),
        ('Retrait documents (banque)', 'Retrait documents (banque)'),
        ('Depot transitaire/Documents', 'Dépôt transitaire/Documents'),
        ('Arrivee marchandise', 'Arrivée marchandise'),
        ('Dedouanement en cours', 'Dédouanement en cours'),
        ('Cheque de douane', 'Chèque de douane'),
        ('Reception marchandise', 'Réception marchandise'),
        ('Accuse de confirmation', 'Accusé de confirmation'),
        ('Reception dossier Transit', 'Récéption dossier Transit'),
        ('Retrait dossier comptable', 'Retrait dossier comptable'),
        ('Terminee', 'Terminée')
    ]

    STATE_TL = [
        ('draft', 'Brouillon'),
        ('confirmation', 'Confirmation'),
        ('production', 'En cours de production'),
        ('expedition', 'Expédition marchandise'),
        ('Récéption documants', 'Récéption documants'),
        ('Retrait documents', 'Retrait documents (banque)'),
        ('Dépôt transitaire/Documents', 'Dépôt transitaire/Documents'),
        ('Arrivee marchandise', 'Arrivée marchandise'),
        ('Dedouanement en cours', 'Dédouanement en cours'),
        ('Cheque de douane', 'Chèque de douane'),
        ('Reception marchandise', 'Réception marchandise'),
        ('Accuse de confirmation', 'Accusé de confirmation'),
        ('Reception dossier Transit', 'Récéption dossier Transit'),
        ('Paiement fournisseur', 'Paiement fournisseur'),
        ('Retrait dossier comptable', 'Retrait dossier comptable'),
        ('Terminee', 'Terminée')
    ]

    STATE_SP = [
        ('draft', 'Brouillon'),
        ('confirmation', 'Confirmation'),
        ('production', 'En cours de production'),
        ('expedition', 'Expédition marchandise'),
        ('Reception documants', 'Récéption documants'),
        ('Depot transitaire/Documents', 'Dépôt transitaire/Documents'),
        ('Arrivee marchandise', 'Arrivée marchandise'),
        ('Dedouanement en cours', 'Dédouanement en cours'),
        ('Cheque de douane', 'Chèque de douane'),
        ('Reception marchandise', 'Réception marchandise'),
        ('Accuse de confirmation', 'Accusé de confirmation'),
        ('Reception dossier Transit', 'Récéption dossier Transit'),
        ('Retrait dossier comptable', 'Retrait dossier comptable'),
        ('Terminee', 'Terminée')
    ]

    state_rd = fields.Selection(selection=STATE_RD, string='État', required=True, readonly=True, copy=False,
                                tracking=True, default='draft')
    state_lc = fields.Selection(selection=STATE_LC, string='État', required=True, readonly=True, copy=False,
                                tracking=True, default='draft')
    state_sp = fields.Selection(selection=STATE_SP, string='État', required=True, readonly=True, copy=False,
                                tracking=True, default='draft')
    state_tl = fields.Selection(selection=STATE_TL, string='État', required=True, readonly=True, copy=False,
                                tracking=True, default='draft')

    state_actuel = fields.Char(
        string='Statut',
        compute="_onchange_payement_"
    )

    @api.onchange('model_id')
    def _onchange_model_id(self):
        # raise UserError("sssssssss")
        lines = []
        for record in self.model_id.product_lines:
            vals = {
                'product_id': record.product_id.id,
                'amount': record.amount
            }
            # lines += [vals]
            lines.append((0, 0, vals))
        if len(lines) > 0:
            self.update({'frais_ids': lines})

    @api.depends('payment_mode')
    def _onchange_payement_(self):
        for record in self:
            if record.payment_mode == 'L.C':
                record.state_actuel = str(dict(record._fields['state_lc'].selection).get(record.state_lc))
            elif record.payment_mode == 'remise_documentaire_vue':
                record.state_actuel = str(dict(record._fields['state_rd'].selection).get(record.state_rd))
            elif record.payment_mode == 'remise_documentaire_echeance':
                record.state_actuel = str(dict(record._fields['state_rd'].selection).get(record.state_rd))
            elif record.payment_mode == 'transfert_libre':
                record.state_actuel = str(dict(record._fields['state_tl'].selection).get(record.state_tl))
            elif record.payment_mode == 'sans_paiement':
                record.state_actuel = str(dict(record._fields['state_sp'].selection).get(record.state_sp))
            else:
                record.state_actuel = ""

    purchase_ids = fields.One2many(
        'purchase.import.folder.purchases', 'folder_id',
        string='Lines')
    product_ids = fields.One2many(
        'purchase.import.folder.products', 'folder_id',
        string='Lines')
    d10_ids = fields.One2many(
        'purchase.import.folder.d10', 'folder_id',
        string='Lines')
    invoice_ids = fields.One2many(
        'purchase.import.folder.invoices', 'folder_id',
        string='Lines')
    frais_ids = fields.One2many(
        'purchase.import.folder.frais', 'folder_id',
        string='Lines')
    detail = fields.Text(string="Détail")
    bank_id = fields.Many2one("res.bank", string="Banque de domiciliation")
    # 2nd LC document exigés
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

    total_invoices = fields.Monetary(string='Total des factures', compute='_get_montant_invoice')
    additionnal_charges = fields.Monetary(string='Charges supplémentaires')
    total = fields.Monetary(string='Total', compute='_get_montant_invoice')
    total_cmd = fields.Monetary(string='Total des commandes', compute='_get_montant_invoice')
    product_designation = fields.Char(string='Produit', compute='_get_products_des')
    total_frais = fields.Monetary(string='Total des frais', compute='_get_montant_invoice')



    def _get_products_des(self):
        for folder in self:
            folder.product_designation = ""
            for line in folder.purchase_ids:
                for lineproduct in line.purchase_id.order_line:
                    folder.product_designation = folder.product_designation + "-" + lineproduct.name

    def _get_montant_invoice(self):
        for folder in self:
            folder.product_designation = ""
            print("odooo")
            for line in folder.invoice_ids:
                folder.total_invoices = folder.total_invoices + line.amount_total
            folder.total_cmd = 0
            for line in folder.purchase_ids:
                print("cccccccccc")
                folder.total_cmd = folder.total_cmd + line.amount_total
                for lineproduct in line.purchase_id.order_line:
                    folder.product_designation = folder.product_designation + "-" + lineproduct.name
            for line in folder.frais_ids:
                folder.total_frais = folder.total_frais + line.amount
                # raise UserError(folder.total)
            # folder.amount_dinars = folder.taux_change * folder.amount_devise
            # folder.amount_douane = (folder.taux_douanes) * folder.amount_dinars
            # folder.amount_tcs = (folder.taux_tcs) * folder.amount_dinars
            # folder.amount_total_d10 = (folder.taux_tva) * (folder.amount_dinars+folder.amount_douane)
            # folder.total = folder.additionnal_charges+folder.total_invoices
            # folder.amount_quitance = folder.amount_total_d10+folder.frais_quitance


    def get_key_actuel(self, val,tuple_list):
        for key, value in tuple_list:
            print(key,value)
            if val == value:
                result = [tup[1] for tup in tuple_list].index(val)
                print(result)
                return result
        return "key doesn't exist"


    def update_list(self):
        lines = []
        self.update({'purchase_ids': None})
        self.update({'invoice_ids': None})
        order_list = self.env['purchase.order'].search([('import_folder', '=', self.id)])
        for val in order_list:
            line_item = {
                'purchase_id': val['id'],
            }
            lines.append([0, 0, line_item])
        self.update({'purchase_ids': lines})
        lines = []
        invoice_list = self.env['account.move'].search([('import_folder', '=', self.id)])
        for val in invoice_list:
            line_item = {
                'invoice_id': val['id'],
            }
            lines.append([0, 0, line_item])
        self.update({'invoice_ids': lines})

        if self.payment_mode == 'L.C':
            if int(self.get_key_actuel(self.state_actuel, self.STATE_LC)) < len(self.STATE_LC):
                new_state = int(self.get_key_actuel(self.state_actuel, self.STATE_LC)) + 1
                new_key = [tup[0] for tup in self.STATE_LC][int(new_state)]
                self.state_lc = new_key
                self.state_actuel = new_key

        elif (self.payment_mode == 'remise_documentaire_vue') or (self.payment_mode == 'remise_documentaire_echeance'):
            key = int(self.get_key_actuel(self.state_actuel, self.STATE_RD))
            if key < len(self.STATE_RD):
                new_state = key+ 1
                new_key = [tup[0] for tup in self.STATE_RD][int(new_state)]
                self.state_rd = new_key

        elif self.payment_mode == 'transfert_libre':
            key = int(self.get_key_actuel(self.state_actuel, self.STATE_TL))
            if key < len(self.STATE_TL):
                new_state = key + 1
                new_key = [tup[0] for tup in self.STATE_TL][int(new_state)]
                self.state_tl = new_key

        elif self.payment_mode == 'sans_paiement':
            key = int(self.get_key_actuel(self.state_actuel, self.STATE_SP))
            if key < len(self.STATE_SP):
                new_state = key + 1
                new_key = [tup[0] for tup in self.STATE_SP][int(new_state)]
                self.state_sp = new_key

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('purchase.import.folder') or 'New'
        result = super(ImportFolder, self).create(vals)
        return result

    # def action_done(self):
    #     self.state = "done"

    # @api.multi
    # def unlink(self):
    #     for order in self:
    #         if order.state not in ('draft'):
    #             raise UserError(_('Vous ne pouvez pas supprimer un élément non brouillon'))
    #     return super(Tourne, self).unlink()


class ImportFolderProducts(models.Model):
    _name = "purchase.import.folder.d10"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "d10_number"

    reception_date = fields.Date(string="Date DE récèption")
    taux_change = fields.Float(string='règlement (Taux de change)', default="1", digits=(12, 5), required=True)
    d10_number = fields.Char(string="NUMERO DE D10", required=True)
    currency_id = fields.Many2one(related='folder_id.currency_id')
    d10_date = fields.Date(string="Date DE D10", required=True)
    quitance_number = fields.Char(string="N° Quitance")
    quitance_date = fields.Date(string="Date de quitance")
    # les taux
    taux_douanes = fields.Float(string='TAUX DE DROITS DOUANIERS', default="5")
    taux_tcs = fields.Float(string='TAUX DE TCS', default="2")
    taux_tva = fields.Float(string='TVA', default="19")
    # les montants
    amount_quitance = fields.Monetary(string='Montant de quitance', compute='_get_montant_invoice')
    frais_quitance = fields.Monetary(string='Frais de quitance')
    amount_devise = fields.Monetary(string='Montant en devise')
    amount_douane = fields.Monetary(string='Droit de douanes', compute='_get_montant_invoice')
    amount_tcs = fields.Monetary(string='TCS', compute='_get_montant_invoice')
    amount_dinars = fields.Float(string='VALEUR EN DA (1)', store=True, compute='_get_montant_invoice')
    amount_total_d10 = fields.Monetary(string='VALEUR EN D10 (2)', compute='_get_montant_invoice')
    total_frais = fields.Monetary(string='Total des frais', compute='_get_montant_invoice')
    debours = fields.Float(string='Débours')
    amount_tva = fields.Float(string='Montant TVA', store=True, compute='_get_montant_invoice')
    fret = fields.Float(string='Fret')
    fret_devise = fields.Float(string='Fret devise')
    frais_douanier = fields.Float(string='Autres frais douanier')
    total_product_price = fields.Float(string='Total prix produits', default=1)
    total_product_poid = fields.Float(string='Total poid', default=0)

    folder_id = fields.Many2one(
        'purchase.import.folder',
        string='Lines', readonly=True)
    product_ids = fields.One2many(
        'purchase.import.folder.d10.products', 'd10_id',
        string='Lines')

    @api.onchange('product_ids')
    def _onchange_product_ids(self):
        for d10 in self:
            d10.total_product_price = 0.0
            d10.total_product_poid = 0.0
            for line in d10.product_ids:
                d10.total_product_price = d10.total_product_price + line.price_da
                d10.total_product_poid = d10.total_product_poid + line.poid
            # for line in d10.product_ids:
            #     d10.product_ids._get_product_prices()

    # def _get_products_amount(self):
    #     for d10 in self:
    #         for line in d10.product_ids:
    #             d10.total_product_price = d10.total_product_price + line.price_da
    #         raise UserError(d10.total_product_price )

    @api.depends('taux_change', 'amount_devise')
    def _get_montant_invoice(self):
        for d10 in self:
            d10.total_frais = 0
            for line in d10.folder_id.frais_ids:
                if d10.id == line.d10.id:
                    d10.total_frais = d10.total_frais + line.amount
            d10.amount_dinars = d10.taux_change * d10.amount_devise
            print(d10.amount_dinars)
            d10.amount_douane = (d10.taux_douanes) * d10.amount_dinars / 100
            d10.amount_tcs = (d10.taux_tcs) * d10.amount_dinars / 100
            amount_tva = int((d10.taux_tva) * (d10.amount_tcs + d10.amount_dinars + d10.amount_douane) / 100)
            d10.amount_tva = amount_tva
            d10.amount_total_d10 = int(amount_tva) + int(d10.amount_tcs) + int(d10.frais_douanier) + int(
                d10.amount_douane)
            d10.amount_quitance = int(d10.amount_total_d10 + d10.frais_quitance)


class ImportFolderD10Products(models.Model):
    _name = "purchase.import.folder.d10.products"

    product_id = fields.Many2one("product.product", string='Produit', required=True)
    folder_id = fields.Many2one(related='d10_id.folder_id', string='Dossier')
    quantity = fields.Float(string="Quantité", required=True)
    poid = fields.Float(string="Poid", required=True)
    price = fields.Float(string="Prix d'achat(Devise)", required=True)
    price_da = fields.Float(string="Prix d'achat DA", readonly=True, compute='_get_product_prices')
    droit_douane = fields.Float(string="Droit douane")
    total = fields.Float(string="Cout d'achat", store=True, compute='_get_product_prices')
    total_tax = fields.Float(string="TCS + DD", compute='_get_product_prices')
    total_charge = fields.Float(string="Total des charges", compute='_get_product_prices')
    cle_repartition = fields.Float(string="Clé de répartition", digits=(12, 2), compute='_get_product_prices')
    charge_reparti = fields.Float(string="Débours répartis", digits=(12, 2), compute='_get_product_prices')
    cout = fields.Float(string="Cout d'achat unitaire", compute='_get_product_prices')
    d10_id = fields.Many2one(
        'purchase.import.folder.d10',
        string='Lines', readonly=True)
    # products
    taux_douanes = fields.Float(string='TAUX DE DROITS DOUANIERS', default="5")
    taux_tcs = fields.Float(string='TAUX DE TCS', default="2")
    amount_douane = fields.Float(string='Droit de douanes', compute='_get_product_prices')
    amount_tcs = fields.Float(string='TCS', compute='_get_product_prices')
    type_produit = fields.Selection([
        ('LOCAL_PET', 'PET Local'),
        ('PET', 'PET'),
        ('PEHD', 'PEHD'),
        ('PDR', 'PDR'),
        ('COLORANT', 'COLORANT')
    ],
        string="Type de produit",
        copy=False
        , required=True)

    # RÉPARTITION SELON LE POIDS
    def _get_product_prices(self):
        for product in self:
            taux_change_d10 = 1
            if product.d10_id.taux_change > 0:
                taux_change_d10 = product.d10_id.taux_change * product.quantity
            total_price_da = 0
            product.price_da = taux_change_d10 * product.price
            if product.d10_id.total_product_poid > 0:
                product.cle_repartition = (product.poid / product.d10_id.total_product_poid) * 100
            amout_taxed = product.price_da + product.d10_id.fret * product.cle_repartition / 100
            product.amount_douane = (product.taux_douanes) * amout_taxed / 100
            product.amount_tcs = (product.taux_tcs) * amout_taxed / 100
            product.total_tax = int(product.amount_tcs) + int(product.amount_douane)
            product.total = amout_taxed + product.total_tax
            product.total_charge = product.d10_id.debours + product.d10_id.frais_quitance + product.d10_id.frais_douanier + product.d10_id.total_frais
            product.charge_reparti = product.total_charge * product.cle_repartition / 100
            if product.quantity > 0:
                product.cout = (product.charge_reparti + product.total) / (product.quantity)
                # raise UserError((product.charge_reparti+product.total ))
                if product.type_produit == 'LOCAL_PET' or product.type_produit == 'PET' or product.type_produit == 'PEHD':
                    product.cout = product.cout / 1000

    # Répartition sur le montant global
    # def _get_product_prices(self):
    #     for product in self:
    #         total_price_da=0
    #         product.price_da = product.d10_id.taux_change * product.price* product.quantity
    #         product.amount_douane = (product.taux_douanes) * product.price_da/100
    #         product.amount_tcs = (product.taux_tcs) * product.price_da/100
    #         amount_tva = int((product.taux_tva) * (product.amount_tcs+product.price_da+product.amount_douane)/100)
    #         product.total_tax = int(product.amount_tcs) +int(product.amount_douane )
    #         product.total = amount_tva+int(product.amount_tcs) +int(product.amount_douane )
    #         product.total_charge = product.d10_id.debours + product.d10_id.fret_devise*product.d10_id.taux_change +product.d10_id.frais_douanier+product.d10_id.total_frais
    #         if product.d10_id.total_product_price>0:
    #             product.cle_repartition = product.price_da/product.d10_id.total_product_price
    #             charge_reparti = product.total_charge*product.cle_repartition
    #             if product.quantity>0:
    #                 product.cout = (charge_reparti+product.price_da+product.total_tax )/product.quantity

    @api.onchange("product_id")
    def _check_product_exist(self):
        is_product_exist = False
        # raise UserError("ssssssssss")
        if self.product_id:
            for orders in self._origin.d10_id.folder_id.purchase_ids:
                for order in orders.purchase_id:
                    for order_line in order.order_line:
                        if order_line.product_id.id == self.product_id.id:
                            is_product_exist = True
            if not is_product_exist:
                raise UserError("Le produit sélèctionné n'existe dans les bons de commandes")


class ImportFolderProducts(models.Model):
    _name = "purchase.import.folder.products"

    product_id = fields.Many2one("product.product", string='Produit')
    folder_id = fields.Many2one(
        'purchase.import.folder',
        string='Lines', readonly=True)


class ImportFolderPurchases(models.Model):
    _name = "purchase.import.folder.purchases"

    purchase_id = fields.Many2one("purchase.order", string='Achat')
    partner_id = fields.Many2one(related='purchase_id.partner_id', string='Partenaire')
    date_order = fields.Datetime(related='purchase_id.date_order', string='Date')
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
    _name = "purchase.import.folder.invoices"

    invoice_id = fields.Many2one("account.move", string='Facture', domain=[('move_type', '=', 'in_invoice')])
    partner_id = fields.Many2one(related='invoice_id.partner_id', string='Partenaire')
    date_invoice = fields.Date(related='invoice_id.date', string='Date')
    state = fields.Selection(
        related='invoice_id.state')
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    amount_total = fields.Monetary(
        related='invoice_id.amount_total')
    folder_id = fields.Many2one(
        'purchase.import.folder',
        string='Lines', readonly=True)


class TypeLivraison(models.Model):
    _name = "purchase.import.livraison.type"
    _rec_name = "desc"

    name = fields.Char(string='Nom')
    desc = fields.Char(string='Déscription')


class MoyenLivraison(models.Model):
    _name = "purchase.import.livraison.moyen"
    _rec_name = "desc"

    name = fields.Char(string='Nom')
    desc = fields.Char(string='Déscription')


class CreditForm(models.Model):
    _name = "purchase.import.credit.forme"
    _rec_name = "desc"

    name = fields.Char(string='Nom')
    desc = fields.Char(string='Déscription')


class PaymentModalite(models.Model):
    _name = "purchase.import.payment.modality"
    _rec_name = "desc"

    name = fields.Char(string='Nom')
    desc = fields.Char(string='Déscription')


class PaymentFrais(models.Model):
    _name = "purchase.import.folder.frais"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product", string='Article')
    amount = fields.Monetary(string='Montant')
    currency_id = fields.Many2one(related='folder_id.currency_id', string="Devise")
    d10 = fields.Many2one('purchase.import.folder.d10', string="D10")
    folder_id = fields.Many2one(
        'purchase.import.folder',
        string='Lines', readonly=True)
