import base64

from odoo import api, fields, models, tools, _, Command
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang

class Montage_demande_credit(models.Model):
    _name = 'montage.demande.credit'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "MONTAGE DE DEMANDE DE CREDIT"
    _rec_name = 'banque'
    name = fields.Char(string='name')
    banque = fields.Many2one('credit.banque', string='Banque')
    agence = fields.Many2one('credit.banque.agence', string='Agence', domain="[('banque.id', '=', banque)]")
    date = fields.Date(string='Date')
    prevision_id = fields.Many2one(string='Prévision', default=lambda self: self.env.context.get('prevision_id'))
    partner_id = fields.Many2one('res.partner', string='Gestionnaire de compte')
    email = fields.Char(string='Adresse mail', compute='_compute_mail', store=True)
    user = fields.Many2one('res.users', string='Utilisateur', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    @api.depends('partner_id')
    def _compute_mail(self):
        for rec in self:
            if rec.partner_id:
                mail_invite = self.env['mail.wizard.invite'].with_context({
                    'default_res_model': 'montage.demande.credit',
                    'default_res_id': rec.id
                }).with_user(self.env.user).create({
                    'partner_ids': [(4, rec.partner_id.id)],
                    'notify': False})
                mail_invite.add_followers()
                rec.email = rec.partner_id.email
            else:
                rec.email = True

    def send_folder(self):
        for rec in self:
            template = self.env.ref('credit_bancaire.email_template_montage')
            return {
                'name': _("Envoyer"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'montage.mail.send',
                'target': 'new',
                'context': {
                    'default_folder_id': self.id,
                    'default_mail_template_id': template.id,
                },
            }


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


class MontageDemandeCreditSend(models.TransientModel):
    _name = 'montage.mail.send'
    _description = "Montage Demande Credit Send"

    company_id = fields.Many2one(comodel_name='res.company', compute='_compute_company_id', store=True)
    demande_credit_ids = fields.Many2many(comodel_name='montage.demande.credit')
    folder_id = fields.Many2one(comodel_name='montage.demande.credit')

    # == PRINT ==
    enable_download = fields.Boolean(compute='_compute_enable_download')
    checkbox_download = fields.Boolean(
        string="Download",
        compute='_compute_checkbox_download',
        store=True,
        readonly=False,
    )

    # == MAIL ==
    enable_send_mail = fields.Boolean(compute='_compute_enable_send_mail')
    checkbox_send_mail = fields.Boolean(
        string="Email",
        compute='_compute_checkbox_send_mail',
        store=True,
        readonly=False,
    )
    mail_template_id = fields.Many2one(
        comodel_name='mail.template',
        string="Utilisé ce modele",
        domain="[('model', '=', 'montage.demande.credit')]",
    )
    mail_lang = fields.Char(
        string="Lang",
        compute='_compute_mail_lang',
    )
    mail_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string="Destinataires",
        compute='_compute_mail_partner_ids',
        store=True,
        readonly=False,
    )
    mail_subject = fields.Char(
        string="Objet",
        compute='_compute_mail_subject_body',
        store=True,
        readonly=False,
    )
    mail_body = fields.Html(
        string="Contenu",
        sanitize_style=True,
        compute='_compute_mail_subject_body',
        store=True,
        readonly=False,
    )
    mail_attachments_widget = fields.Json(
        compute='_compute_mail_attachments_widget',
        store=True,
        readonly=False,
    )

    @api.model
    def _get_mail_default_field_value_from_template(self, mail_template, lang, demande_credit, field, **kwargs):
        if not mail_template:
            return
        return mail_template\
            .with_context(lang=lang)\
            ._render_field(field, demande_credit.ids, **kwargs)[demande_credit._origin.id]

    def _get_default_mail_lang(self, demande_credit, mail_template=None):
        return mail_template._render_lang([demande_credit.id]).get(demande_credit.id) if mail_template else get_lang(self.env).code

    def _get_default_mail_body(self, demande_credit, mail_template, mail_lang):
        return self._get_mail_default_field_value_from_template(
            mail_template,
            mail_lang,
            demande_credit,
            'body_html',
            options={'post_process': True},
        )

    def _get_default_mail_subject(self, demande_credit, mail_template, mail_lang):
        return self._get_mail_default_field_value_from_template(
            mail_template,
            mail_lang,
            demande_credit,
            'subject',
        )

    def _get_default_mail_partner_ids(self, demande_credit, mail_template, mail_lang):
        partners = self.env['res.partner'].with_company(demande_credit.company_id)
        if mail_template.email_to:
            for mail_data in tools.email_split(mail_template.email_to):
                partners |= partners.find_or_create(mail_data)
        if mail_template.email_cc:
            for mail_data in tools.email_split(mail_template.email_cc):
                partners |= partners.find_or_create(mail_data)
        if mail_template.partner_to:
            partner_to = self._get_mail_default_field_value_from_template(mail_template, mail_lang, demande_credit, 'partner_to')
            partner_ids = mail_template._parse_partner_to(partner_to)
            partners |= self.env['res.partner'].sudo().browse(partner_ids).exists()
        return partners

    def _get_default_mail_attachments_widget(self, demande_credit, mail_template):
       return self._get_placeholder_mail_attachments_data(demande_credit) \
            + self._get_mail_template_attachments_data(mail_template)

    def _get_wizard_values(self):
        self.ensure_one()
        return {
            'mail_template_id': self.mail_template_id.id,
            'download': self.checkbox_download,
            'send_mail': self.checkbox_send_mail,
        }

    def _get_mail_demande_credit_values(self, demande_credit, wizard=None):
        mail_template_id = demande_credit.send_and_print_values and demande_credit.send_and_print_values.get('mail_template_id')
        mail_template = wizard and wizard.mail_template_id or self.env['mail.template'].browse(mail_template_id)
        mail_lang = self._get_default_mail_lang(demande_credit, mail_template)

        return {
            'mail_template_id': mail_template,
            'mail_lang': mail_lang,
            'mail_body': wizard and wizard.mail_body or self._get_default_mail_body(demande_credit, mail_template, mail_lang),
            'mail_subject': wizard and wizard.mail_subject or self._get_default_mail_subject(demande_credit, mail_template, mail_lang),
            'mail_partner_ids': wizard and wizard.mail_partner_ids or self._get_default_mail_partner_ids(demande_credit, mail_template, mail_lang),
            'mail_attachments_widget': wizard and wizard.mail_attachments_widget or self._get_default_mail_attachments_widget(demande_credit, mail_template),
        }

    def _get_placeholder_mail_attachments_data(self, demande_credit):
        #if demande_credit.credit_pdf_report_id:
        return []

        filename = demande_credit._get_credit_report_filename()
        return [{
            'id': f'placeholder_{filename}',
            'name': filename,
            'mimetype': 'application/pdf',
            'placeholder': True,
        }]

    """@api.model
    def _get_demande_credit_extra_attachments(self, demande_credit):
        #return demande_credit.credit_pdf_report_id
        return False"""

    def generate_and_attach_report(self):
        print('generate')
        self.ensure_one()
        self.env['ir.attachment'].search([('res_id', '=', self.folder_id.id),
                                          ('res_model', '=', 'montage.demande.credit')]).unlink()
        self.mail_template_id.attachment_ids = False
        report_service = 'credit_bancaire.montage_plan_charge_report'
        pdf_content, content_type = self.env['ir.actions.report']._render_qweb_pdf(report_service, [self.folder_id.id])
        attachment = self.env['ir.attachment'].create({
            'name': f'{self.folder_id.banque.name } Plan des charges.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'montage.demande.credit',
            'res_id': self.folder_id.id,
            'mimetype': 'application/pdf',
        })
        attach_list = []
        attach_list.append(attachment.id)

        report_service = 'credit_bancaire.montage_plan_appro_report'
        pdf_content, content_type = self.env['ir.actions.report']._render_qweb_pdf(report_service, [self.folder_id.id])
        attachment = self.env['ir.attachment'].create({
            'name': f'{self.folder_id.banque.name } Plan d\'approvisionnement.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'montage.demande.credit',
            'res_id': self.folder_id.id,
            'mimetype': 'application/pdf',
        })
        attach_list.append(attachment.id)
        report_service = 'credit_bancaire.montage_plan_importation_report'
        pdf_content, content_type = self.env['ir.actions.report']._render_qweb_pdf(report_service, [self.folder_id.id])
        attachment = self.env['ir.attachment'].create({
            'name': f'{self.folder_id.banque.name } Plan d\'importation.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'montage.demande.credit',
            'res_id': self.folder_id.id,
            'mimetype': 'application/pdf',
        })
        attach_list.append(attachment.id)
        self.mail_template_id.attachment_ids = self.env['ir.attachment'].browse(attach_list)

    """@api.model
    def _get_demande_credit_extra_attachments_data(self, demande_credit):

        return [
            {
                'id': attachment.id,
                'name': attachment.name,
                'mimetype': attachment.mimetype,
                'placeholder': False,
                'protect_from_deletion': True,
            }
            for attachment in self._get_demande_credit_extra_attachments(demande_credit)
        ]"""

    @api.model
    def _get_mail_template_attachments_data(self, mail_template):
        self.generate_and_attach_report()
        return [
            {
                'id': attachment.id,
                'name': attachment.name,
                'mimetype': attachment.mimetype,
                'placeholder': False,
                'mail_template_id': mail_template.id,
            }
            for attachment in mail_template.attachment_ids
        ]

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('demande_credit_ids')
    def _compute_company_id(self):
        for wizard in self:
            if len(wizard.demande_credit_ids.company_id) > 1:
                raise UserError(_("You can only send from the same company."))
            wizard.company_id = wizard.demande_credit_ids.company_id.id

    @api.depends('demande_credit_ids')
    def _compute_enable_download(self):
        for wizard in self:
            wizard.enable_download = bool(wizard.demande_credit_ids)

    @api.depends('enable_download')
    def _compute_checkbox_download(self):
        for wizard in self:
            wizard.checkbox_download = wizard.enable_download and wizard.company_id.invoice_is_download

    @api.depends('demande_credit_ids')
    def _compute_enable_send_mail(self):
        for wizard in self:
            wizard.enable_send_mail = bool(wizard.demande_credit_ids)

    @api.depends('enable_send_mail')
    def _compute_checkbox_send_mail(self):
        for wizard in self:
            wizard.checkbox_send_mail = wizard.company_id.invoice_is_email and not wizard.send_mail_readonly

    @api.depends('checkbox_send_mail')
    def _compute_mail_lang(self):
        for wizard in self:
            wizard.mail_lang = wizard.company_id.partner_id.lang or get_lang(self.env).code

    @api.depends('folder_id')
    def _compute_mail_partner_ids(self):
        for wizard in self:
                partners = self.env['res.partner']
                partners |= wizard.folder_id.partner_id
                wizard.mail_partner_ids = partners

    @api.depends('mail_template_id')
    def _compute_mail_subject_body(self):
        for wizard in self:
            demande_credit = wizard.folder_id
            mail_template = wizard.mail_template_id
            mail_lang = wizard.mail_lang
            wizard.mail_subject = self._get_default_mail_subject(demande_credit, mail_template, mail_lang)
            wizard.mail_body = self._get_default_mail_body(demande_credit, mail_template, mail_lang)

    @api.depends('folder_id')
    def _compute_mail_attachments_widget(self):
        for wizard in self:
            if wizard.folder_id:
                demande_credit = wizard.folder_id
                mail_template = wizard.mail_template_id
                wizard.mail_attachments_widget = self._get_default_mail_attachments_widget(demande_credit, mail_template)

    def action_send_and_print(self):
        self.ensure_one()
        email_template = self.mail_template_id

        email_template.send_mail(self.folder_id.id, force_send=True)

