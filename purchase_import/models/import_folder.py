# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta

class ImportStage(models.Model):
    _name = 'import.stage'
    _description = 'import Stage'
    _order = "id, sequence"




   
    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(required=True)
   

class ImportFolder(models.Model):
    _name = "purchase.import.folder"
    _inherit = ["mail.thread",'mail.activity.mixin','mail.tracking.duration.mixin']
    _rec_name = "reference"
    _track_duration_field = 'stage_id'

    #champs principale
    reference = fields.Char(string='N. Commande')
    note = fields.Text(string='Note')
    proformat = fields.Char(string="Proforma")
    montant_proformat = fields.Float(string="Montant de Proforma")
    designation_marchandise = fields.Text(string="Designation de marchandise")
    # tarif_id = fields.Many2one('import.tarif', string='Tarif douanier')
    tarif =  fields.Char(string='Tarif douanier')
    partner_id = fields.Many2one("res.partner", string='Fournisseur',
                                 domain="[('partner_type', '=', 'supplier'),('supplier_type', '=', 'etranger')]")
    #transitaire_id = fields.Many2one("res.partner", string='Transitaire')
    date_usine = fields.Date(string="Date d'arrivage")
    currency_id = fields.Many2one(
       'res.currency', string="Devise", company_dependent=True,
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    date = fields.Date(string='Date')
    date_embarquement = fields.Date(string="Date d'embarquement")
    date_reception_validation = fields.Date(string="Date réception fiche validation")
    date_reception_attestation = fields.Date(string="Date réception attestation de régulation")
    date_proforma_dom = fields.Date(string="Date Dom. Proforma")
    num_commande = fields.Char(string='Numéro de commande')
    payment_mode = fields.Selection([
        ('LC_a_vue', 'LC à vue'),
        ('LC_a_DP', 'LC à DP'),
        ('REMDOC_a_vue', 'REMDOC à vue'),
        ('REMDOC_a_DP', 'REMDOC à DP'),
        ('transfert_libre_a_vue', 'Transfert libre à vue'),
        ('transfert_libre_a_DP', 'Transfert libre à DP'),
    ],
        default='LC_a_vue',
        string="Mode de paiement",
        copy=False)
    sans_dom = fields.Boolean('Sans Dom. ?')
    # state_actuel = fields.Char(
    #     string='Statut',
    #     compute="_onchange_state_"
    # )
    

    # Champs importations
    port_embarquement = fields.Char(string="Port d'embarquement")
    navire = fields.Char(string='Navire')
    compagnieie_maritime = fields.Char(string='Compagnie maritime')
    n_bl = fields.Char(string='N° B/L')
    etd = fields.Char(string='ETD')
    eta = fields.Char(string='ETA')
    tracking_doc = fields.Char(string='Tracking Doc')
    stage = fields.Integer(compute='compute_stage')

    #champs du detail de Dom
    bank_id = fields.Many2one("credit.banque", string="Banque de domiciliation", domain="[('journal_id', '!=', False)]")
    reference_dossier_banque = fields.Char(string="Numéro de Dom.")
    date_ouverture_lc = fields.Date(string="Date d`ouverture LC")
    montant = fields.Monetary(string="Montant")
    montant_dz = fields.Monetary(string='Montant DZD.')
    incoterm = fields.Many2one('account.incoterms',string="Incoterm")
    methode_expedition = fields.Selection([('by_sea','voie maritime'),('by_air','voie aérienne')],string="Méthode d`expédition", default="by_sea")
    provision_ouverture = fields.Char(string="Provision d`ouverture")
    date_limit_embarquement = fields.Date(string="Date limite d'embarquement")
    date_reception_document = fields.Date(string="Date de réception de document")
    date_report_dom = fields.Date(string="Date Report DOM")
    date_demande_predom = fields.Date(string="Date demande Prédom.")
    date_accord_predom = fields.Date(string="Date accord Prédom.")
  
    
    #SPOT REFIN
    deblocage_spot_refin = fields.Boolean(string="Déblocage SPOT Refin")
    montant_debloque_spot_refin = fields.Monetary(string="montant débloqué")
    date_deblocage_spot_refin = fields.Date(string="Date de déblocage SPOT Refin")
    date_echeance_spot_refin = fields.Date(string="Date d`échéance SPOT Refin")
    reference_deblocage_spot_refin = fields.Char(string="Référence déblocage SPOT Refin")
    montant_a_rembourser_spot_refin = fields.Monetary(string="Montant à rembourser SPOT Refin")

    #SPOT PREFIN
    deblocage_spot_prefin = fields.Boolean(string="Déblocage SPOT Prefin")
    montant_debloque_spot_prefin = fields.Float(string="montant débloqué",)
    date_deblocage_spot_prefin = fields.Date(string="Date de déblocage SPOT Prefin")
    date_echeance_spot_prefin = fields.Date(string="Date d`échéance SPOT Prefin")
    reference_deblocage_spot_prefin = fields.Char(string="Référence déblocage SPOT Prefin")
    montant_a_rembourser_spot_prefin = fields.Monetary(string="Montant à rembourser SPOT Prefin")

    #douane
    montant_droits_douane = fields.Float(string="Montant droits de douane")
    financement_droits_douane = fields.Boolean(string="Financement droits de douane")
    date_deblocage_fin_douane = fields.Date(string="Date de déblocage Fin.Douane")
    date_echeance_fin_douane = fields.Date(string="Date d`échéance Fin.Douan")
    reference_deblocage_fin_douane = fields.Char(string="Référence déblocage Fin.Douane")
    montant_a_rembourser_fin_douane = fields.Monetary(string="Montant a rembourser Fin.Douane")
    facture_file = fields.Binary(string='Facture proforma')
    validation_file = fields.Binary(string='Fiche de validation')
    divers_file = fields.Binary(string='Divers Documents Orignaux')
    #restitution de provision
    restitution_de_provision = fields.Boolean(string="Restitution de Provision", default=False)
    #si restitution de provision est vrai
    montant_restitue = fields.Monetary(string="Montant restitué")
    commission_banque_1 = fields.Char(string="Commission banque 01 ")
    commission_banque_2 = fields.Char(string="Commission banque 02 ")
    commission_banque_3 = fields.Char(string="Commission banque 03 ")
    commission_banque_4 = fields.Char(string="Commission banque 04 ")

    activation_cur = fields.Char(compute='activate_currencies',store=True)
    deblocage_id = fields.Many2one('credit.operation.deb', string='Deblocage')
    ref_facture = fields.Char(string='N. facture', related='deblocage_id.ref_interne')
    delai_payment = fields.Integer(string='Délai de paiement')
    date_payment = fields.Date(string='Date de paiement de fournisseur')
    date_reception_d10 = fields.Date(string='Date de réception D10')
    attach_d10 = fields.Binary(string='Attacher D10')
    date_validation = fields.Date(string='Date de validation')
    payment_id = fields.Many2one('account.payment', string='Référence Paiement')
    journal_id = fields.Many2one('account.journal', string='Journal', related='bank_id.journal_id')
    douane_id = fields.Many2one('credit.operation.deb',
                                string='Financement droit de douane',
                                domain="[('banque_id', '=', bank_id)]")
    provision_id = fields.Many2one('account.payment', string='Provision d\'ouverture',
                                   domain="[('autre_type', '=', 'provision'), ('journal_id', '=', journal_id), ('lc_id', '=', id)]")
    depot_taxe_date = fields.Date(string='Date dépôt taxe de Dom.')
    recuperation_taxe_date = fields.Date(string='Date de récupération')
    echeance_date_lc = fields.Date(string='Date échéance LC')
    date_envoi_draft = fields.Date(string='Date envoie Draft')
    date_confirm_draft = fields.Date(string='Date confirmation Draft')
    date_reception_swift = fields.Date(string='Date réception Swift')
    note = fields.Text('Observations')

    def compute_stage(self):
        for rec in self:
            if rec.stage_id:
                rec.stage = rec.stage_id.sequence
            else:
                rec.stage = 1

    def create_payment(self):
        for rec in self:
            view_id = self.env.ref('account.view_account_payment_form').id
            context = {'dossier_id': rec.id,
                       'default_partner_type': 'supplier',
                       'default_type_supplier': 'local',
                       'default_payment_type': 'outbound',
                       'default_journal_id': rec.bank_id.journal_id.id}
            return {
                'type': 'ir.actions.act_window',
                'name': _('Paiement'),
                'view_mode': 'form',
                'res_model': 'account.payment',
                'target': 'new',
                'view_id': view_id,
                'context': context,
            }

    @api.depends('payment_mode')
    def activate_currencies(self):
        for rec in self:
            cur = rec.env['res.currency'].search([])
            print(len(cur))
    #fonction renvoi la cle d'etat actuel
    def get_key_actuel(self, val):
        for key, value in self.nouv_list:
            if val == value:
                return key
        return "key doesn't exist"



    # #la fonction du bouton suivant
    # def action_suivant(self):
    #     if int(self.get_key_actuel(self.state_actuel)) < len(self.nouv_list):
    #         new_state = int(self.get_key_actuel(self.state_actuel))+1
    #         self.etat = str(new_state)
    #         self._onchange_state_
    #         print("ca marche"+self.etat)
    #         print("get_keys"+self.get_key_actuel(self.state_actuel)+" dddd"+self.state_actuel)

    # #la fonction du bouton precedent
    # def action_precedent(self):
    #     if int(self.get_key_actuel(self.state_actuel)) > 1:
    #         new_state = int(self.get_key_actuel(self.state_actuel))-1
    #         self.etat = str(new_state)
    #         self._onchange_state_
    #         print("ca marche"+self.etat)
    #         print("get_keys"+self.get_key_actuel(self.state_actuel)+" dddd"+self.state_actuel)

    nouv_list = [
        ('0', 'Réception fiche validation'),
        ('1', 'Établissement Taxe Dom.'),
        ('2', 'Domiciliation'),
        ('3', 'Report Dom.'),
        ('4', 'Paiement fournisseur'),
        ('5', 'Clôturé ')
    ]
    # etat = fields.Selection(selection=nouv_list, string="etat",required=True, readonly=True, copy=False,
    #                             tracking=True, default='0')
    stage_id = fields.Many2one('import.stage', string="etat",
                                tracking=True, default=lambda self: self.env.ref('purchase_import.stage_01'))

    '''@api.onchange('model_id')
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
            self.update({'frais_ids': lines})'''


    # def _onchange_state_(self):
    #     for record in self:
    #         record.state_actuel = str(dict(record._fields['etat'].selection).get(record.etat))


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

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('purchase.import.folder') or 'New'
        res = super(ImportFolder, self).create(vals)
        print('deblocage', self.env.context.get('deblocage'))
        if self.env.context.get('deblocage'):
            res.deblocage_id = self.env['credit.operation.deb'].browse(self.env.context.get('deblocage'))
            res.deblocage_id.folder_id = res.id
            res.montant_debloque_spot_prefin = res.deblocage_id.montant_debloque
        return res

    # def action_done(self):
    #     self.state = "done"

    # @api.multi
    # def unlink(self):
    #     for order in self:
    #         if order.state not in ('draft'):
    #             raise UserError(_('Vous ne pouvez pas supprimer un élément non brouillon'))
    #     return super(Tourne, self).unlink()
    

    @api.model
    def notify_users_due_payment(self):
       
        target_date = fields.Date.today() + timedelta(days=20)

     
        import_folders = self.search([('date_payment', '=', target_date)])

        if import_folders:
            group = self.env.ref('purchase_import.group_importation_user')
            users = group.users

            
            for folder in import_folders:
                for user in users:
                   
                    self.env['mail.activity'].create({
                        'res_model_id': self.env['ir.model']._get('purchase.import.folder').id,
                        'res_id': folder.id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,  
                        'summary': 'Paiement dû dans 20 jours',
                        'note': f'Paiement pour le dossier {folder.name} dû  dans 20 jours',
                        'user_id': user.id,
                    })

class ImportFolderProducts(models.Model):
    _name = "purchase.import.folder.d10"
    _rec_name = "d10_number"

    reception_date = fields.Date(string="Date DE réception")
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
            product.cout = 0
            if product.quantity > 0:
                product.cout = (product.charge_reparti + product.total) / product.quantity
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
            print('jjjjjjjj')
            for orders in self.d10_id.folder_id.purchase_ids:
                print('hhhhhhhh')
                for order in orders.purchase_id:
                    for order_line in order.order_line:
                        if order_line.product_id.id == self.product_id.id:
                            print('iiiiiiiiii')
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
    name = fields.Char(string='Réf. Facture')
    date_invoice = fields.Date( string='Date')
    state = fields.Selection(
        related='invoice_id.state')
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    amount_total = fields.Float(string='Montant')
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
