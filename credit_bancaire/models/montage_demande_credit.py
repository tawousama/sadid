from odoo import api, fields, models, _


class Montage_demande_credit(models.Model):
    _name = 'montage.demande.credit'
    _description = "MONTAGE DE DEMANDE DE CREDIT"

    name = fields.Char(string='name')
    date = fields.Date(string='Date')
    prevision_id = fields.Many2one(string='Prévision', default=lambda self: self.env.context.get('prevision_id'))

    @api.model
    def create(self, vals):
        parent_id = self.env.context.get('prevision_id')
        print(parent_id)
        if parent_id:
            vals['prevision_id'] = parent_id
        res = super(Montage_demande_credit, self).create(vals)
        return res

    def open_plan_charge(self):
        for rec in self:
            view_id = self.env.ref('credit_bancaire.view_montage_plan_charges_tree').id
            return {
                'name': 'Plan des Charges',
                'domain': [('montage_demande_credit', '=', rec.id)],
                'res_model': 'montage.plan.charges',
                'view_mode': 'tree',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id}
            }

    def open_plan_local(self):
        for rec in self:
            view_id = self.env.ref('credit_bancaire.view_montage_plan_appro_local_tree').id
            return {
                'name': "Plan d'approvisionnement local",
                'domain': [('montage_demande_credit', '=', rec.id)],
                'res_model': 'montage.plan.appro.local',
                'view_mode': 'tree',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id}
            }

    def open_plan_import(self):
        for rec in self:
            view_id = self.env.ref('credit_bancaire.view_montage_plan_importation_tree').id
            return {
                'name': "Plan d'importation",
                'domain': [('montage_demande_credit', '=', rec.id)],
                'res_model': 'montage.plan.importation',
                'view_mode': 'tree',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id}
            }

    def open_saisi_donnee(self):
        for rec in self:
            view_id = self.env.ref('credit_bancaire.view_montage_saisi_donnee_tree').id
            return {
                'name': "Saisi des données",
                'domain': [('montage_demande_credit', '=', rec.id)],
                'res_model': 'montage.saisi.donnee',
                'view_mode': 'tree',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id}
            }

    def open_variation(self):
        for rec in self:
            view_id = self.env.ref('credit_bancaire.view_montage_variation_poste_comptable_tree').id
            return {
                'name': "Saisi des données",
                'domain': [('montage_demande_credit', '=', rec.id)],
                'res_model': 'montage.variation.poste.comptable',
                'view_mode': 'tree',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'context': {'parent_id': rec.id}
            }


class Plan_charges(models.Model):
    _name = 'montage.plan.charges'
    _description = "PLAN DES CHARGES"

    name = fields.Char(string='name')
    type_marche = fields.Selection([('attribue', 'Attribué'),
                                    ('en_realisation','En réalisation'),
                                    ('en_signature', 'En signature'),
                                    ('signe', 'Signé')],
                                   string="Type de marché")
    maitre_ouvrage = fields.Many2one('res.partner', string="Maitre de l'ouvrage", store=True)
    domiciliation_bancaire = fields.Many2one('credit.banque',string='Domiciliation Bancaire', store=True)
    montant_ht = fields.Float(string='Montant H.T')
    objet_marche = fields.Char(string='Objet du marché')
    date_ods = fields.Date(string='Date d`ODS',tracking=True)
    delai_realisation = fields.Integer(string='Délai de réalisation (mois)')
    cbe = fields.Boolean(string='CBE')
    montant_cbe = fields.Float(string='Montant CBE')
    caution_cra = fields.Boolean(string='Caution CRA')
    montant_cra = fields.Float(string='Montant CRA')
    taux_avancement = fields.Float(string='Taux d`avancement')
    paiement_encaisse_ht = fields.Float(string='Paiements encaissés H.T')
    paiement_attendu_ht = fields.Float(string='Paiements attendus H.T')
    montage_demande_credit = fields.Many2one('montage.demande.credit', store=True)

    @api.model
    def create(self, vals):
        parent_id = self.env.context.get('parent_id')
        print(parent_id)
        if parent_id:
            vals['montage_demande_credit'] = parent_id
        res = super(Plan_charges, self).create(vals)
        return res


class Plan_appro_local(models.Model):
    _name = 'montage.plan.appro.local'
    _description = "PLAN D`APPRO LOCAL"

    nature_marchandise = fields.Many2one('product.product',string='Nature de marchandise')
    fournisseur = fields.Many2one('res.partner',string='Nom du fournisseur')
    mode_reglement = fields.Selection([('espece','Espèce'),
                                       ('cheque','Chèque'),
                                       ('virement','Virement'),
                                       ('mixe','Mixe')],string='Mode de reglement')
    type_reglement = fields.Char(string='Type de reglement (avue a terme)')
    montant_previsionnel = fields.Float(string='Montant prévisionnel H.T')
    date_previsionnel = fields.Date(string='Date prévisionnelle du lancement de commande')
    delai_moyen_livraision = fields.Integer(string='Délai moyen de livraison (en jours)')
    montage_demande_credit = fields.Many2one('montage.demande.credit', store=True)

    @api.model
    def create(self, vals):
        parent_id = self.env.context.get('parent_id')
        print(parent_id)
        if parent_id:
            vals['montage_demande_credit'] = parent_id
        res = super(Plan_appro_local, self).create(vals)
        return res


class Plan_importation(models.Model):
    _name = 'montage.plan.importation'
    _description = "PLAN D`IMPORTATION"

    marchandise_importer = fields.Many2one('product.product',string='Marchandises à importer')
    fournisseur = fields.Many2one('res.partner',string='Fournisseur')
    pays_fournisseur = fields.Many2one('res.country',string='Pays de fournisseur')
    banque_fournisseur = fields.Char(string='Banque du fournisseur')
    mode_paiement = fields.Selection([
        ('LC_a_vue', 'LC à vue'),
        ('LC_a_DP', 'LC à DP'),
        ('REMDOC_a_vue', 'REMDOC à vue'),
        ('REMDOC_a_DP', 'REMDOC à DP'),
        ('transfert_libre', 'Transfert libre'),
    ],
        string="Mode de paiement")
    currency_id = fields.Many2one(
        'res.currency', string="Devise", company_dependent=True,
        help="This currency will be used, instead of the default one, for purchases from the current partner")
    montant_devise = fields.Float(string='Montant en devise')
    montant_DZD = fields.Float(string='Montant en DZD', compute='_compute_montant_dzd')
    tarif_douanier = fields.Float(string='Tarif douanier')
    montant_global_DZD = fields.Float(string='Montant global DZD', compute='_compute_montant_global_dzd')
    lead_time = fields.Integer(string='Lead Time (délai entre la Dom.Bancaire et l`arrivée de marchandise). En jours')
    date_lancement_commande = fields.Date(string='Date prévisionnelle du lancement de commande')
    montage_demande_credit = fields.Many2one('montage.demande.credit', store=True)

    @api.model
    def create(self, vals):
        parent_id = self.env.context.get('parent_id')
        print(parent_id)
        if parent_id:
            vals['montage_demande_credit'] = parent_id
        res = super(Plan_importation, self).create(vals)
        return res

    @api.depends('currency_id', 'montant_devise')
    def _compute_montant_dzd(self):
        for rec in self :
            change = rec.currency_id.rate
            rec.montant_DZD = rec.montant_devise * change

    @api.depends('tarif_douanier', 'montant_DZD')
    def _compute_montant_global_dzd(self):
        for rec in self :
            plus = rec.montant_DZD * rec.tarif_douanier
            rec.montant_global_DZD = rec.montant_DZD + plus


class Saisi_donnees(models.Model):
    _name = 'montage.saisi.donnee'
    _description = "SAISI DES DONNEES"

    poste = fields.Char(string='Poste')
    n_2 = fields.Float(string='N_2')
    n_1 = fields.Float(string='N_1')
    montage_demande_credit = fields.Many2one('montage.demande.credit', store=True)

    @api.model
    def create(self, vals):
        parent_id = self.env.context.get('parent_id')
        print(parent_id)
        if parent_id:
            vals['montage_demande_credit'] = parent_id
        res = super(Saisi_donnees, self).create(vals)
        return res


class Variation_poste_comptable(models.Model):
    _name = 'montage.variation.poste.comptable'
    _description = "VARIATIONS DES POSTES COMPTABLES"

    poste = fields.Char(string='Poste',readonly=True)
    n_2 = fields.Float(string='N_2',compute='_compute_n2')
    n_1 = fields.Float(string='N_1',compute='_compute_n1')
    variation = fields.Float(string='Var.%', compute='_compute_variation')
    explication = fields.Char(string='Explications')
    montage_demande_credit = fields.Many2one('montage.demande.credit', store=True)

    @api.model
    def create(self, vals):
        parent_id = self.env.context.get('parent_id')
        print(parent_id)
        if parent_id:
            vals['montage_demande_credit'] = parent_id
        res = super(Variation_poste_comptable, self).create(vals)
        return res

    @api.depends('poste')
    def _compute_n2(self):
        for rec in self:
            donnee = rec.env['montage.saisi.donnee'].search([])
            print(donnee)
            for d in donnee:
                if d.poste == rec.poste:
                    rec.n_2 = d.n_2

    @api.depends('poste')
    def _compute_n1(self):
        for rec in self:
            donnee = rec.env['montage.saisi.donnee'].search([])
            print(donnee)
            for d in donnee:
                if d.poste == rec.poste:
                    rec.n_1 = d.n_1

    def _compute_variation(self):
        for rec in self:
            if rec.n_2 != 0:
                rec.variation = (rec.n_1 - rec.n_2) / rec.n_2
            else: rec.variation = 0



