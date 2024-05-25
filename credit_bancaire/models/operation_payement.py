from odoo import api, fields, models, _

from odoo.exceptions import ValidationError


class Gestion_payement(models.Model):
    _name = 'credit.operation.p'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Opérations bancaire"

    name = fields.Char(string='Opération', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    user_id = fields.Many2one(
        'res.users', string='Order representative', index=True, tracking=True, readonly=True,
        default=lambda self: self.env.user, check_company=True)

    ref_opr_deb = fields.Many2one('credit.operation.deb', string='Opération de déblocage', ondelete='cascade',domain="[('banque_id.id', '=', banque),('type.id', '=', type),('ligne_autorisation.id', '=', ligne_autorisation),]",)
    montant_echeance = fields.Float(string="`Montant de l`échéance", store=True, compute='_compute_montant_echeance')
    banque = fields.Many2one(
        'credit.banque', string='Banque',  index=True, tracking=True, required=True)
    type = fields.Many2one(
        'credit.type', string='Ligne de crédit', index=True, tracking=True,compute="_compute_type")
    ligne_autorisation = fields.Many2one('credit.autorisation', string='Autorisation',domain="[('banque.id', '=', banque),('type.id', '=', type)]", required=True,ondelete='cascade',compute='_compute_ligne_autorisation' )
    state = fields.Selection([('draft', 'Brouillon'),
                              ('confirmed', 'Confirmé')], default='draft')
    date_create = fields.Datetime(string='Date de création', required=True, index=True, copy=False,
                                  default=fields.Datetime.now,
                                  help="Indicates the date the operation p was created.",
                                  readonly=True)
    date_echeance = fields.Date("Date d`échéance", tracking=True, required=True,compute='_compute_date_echeance')
    date_deblocage = fields.Date("Date de déblocage", tracking=True,compute='_compute_date_deblocage')
    reference_dossier = fields.Char(string='Référence du dossier banque', tracking=True,readonly=True, compute='_compute_dossier_reference')
    fournisseur = fields.Many2one('res.partner', string='Client / Fournisseur', index=True, tracking=True,readonly=True, compute='_compute_fournisseur')
    facture = fields.Many2one('account.move', string='N. facture', tracking=True,readonly=True, compute='_compute_facture')
    montant_a_rembourser = fields.Float(string="Montant à rembourser", store=True,readonly=True, compute='_compute_montant_rembourser')
    paiements = fields.One2many('credit.operation.paiementdetail','paiement_global')
    echeance = fields.Many2one('credit.operation.deb.echeance',index=True, tracking=True,store=True, ondelete="cascade")
    montant_paye = fields.Float(string="Montant paye", store=True,readonly=True, compute='_compute_montant_paye')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.operation.p') or _('New')
        result = super(Gestion_payement, self).create(vals)
        return result

    def validate_payment(self):
        for rec in self:
            if not rec.date_echeance:
                rec.date_echeance = fields.Date.today()
            if rec.state == 'draft':
                rec.state = 'confirmed'
            view_id = self.env.ref('credit_bancaire.deblocage_wizard_form').id
            return {
                'name': 'Information',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'wizard.credit.deblocage',
                'view_id': view_id,
                'target': 'new',
                'context': {'payment': rec.id,
                            'deb_id': rec.ref_opr_deb.id},
            }

    def unlink(self):
        for rec in self:
            if len(rec.paiements) != 0:
                raise ValidationError(_("Vous devriez d`abord supprimer les lignes de paiements "))
            else:
                return super(Gestion_payement, self).unlink()


    @api.depends('paiements')
    def _compute_montant_rembourser(self):
        for rec in self:
            sum = 0
            remb = rec.ref_opr_deb.montant_total
            ttl_remb = 0
            paims = rec.env['credit.operation.p'].search([('ref_opr_deb', '=', rec.ref_opr_deb.id)])
            if paims:
                for i in paims:
                    ttl_remb += i.montant_paye
            paim = rec.env['credit.operation.paiementdetail'].search([('paiement_global', '=', rec.id)])
            print(paim)
            if paim:
                for p in paim:
                    sum += p.montant_paye
                    print(str(p.id)+' '+str(sum))

                deblocage = rec.env['credit.operation.deb'].search([('id', '=', rec.ref_opr_deb.id)])
                disponible = rec.env['credit.disponible'].search(
                    [('ligne_autorisation', '=', rec.ligne_autorisation.id)])
                print(disponible.montant_disponible)
                print('il existe echeance partie ---- '+str(rec.echeance.id))
                if rec.echeance:
                    echeance_partiel = deblocage.env['credit.operation.deb.echeance'].search([('id','=',rec.echeance.id)])
                    echeance = rec.env['credit.echeance'].search([('echeance', '=', echeance_partiel.id)])
                    ecart = echeance_partiel.montant_total - rec.montant_a_rembourser
                    print(echeance_partiel.montant_total)
                    echeance_partiel.montant_rembourser = echeance.montant_a_rembourser = echeance_partiel.montant_total - sum
                    rec.montant_a_rembourser = echeance_partiel.montant_total - sum
                else:
                    ecart = rec.ref_opr_deb.montant_total - rec.montant_a_rembourser
                    rec.montant_a_rembourser = remb - sum
                    echeance = rec.env['credit.echeance'].search([('ref_opr_deb', '=', rec.ref_opr_deb.id)])
                    echeance.montant_a_rembourser = remb - sum
                mont_dispo=disponible.montant_disponible + sum - ecart
                print('remb = '+str(remb))
                print('ttl_remb = ' + str(ttl_remb))
                print('ecart = ' + str(ecart))
                print('sum = ' + str(sum))
                print(mont_dispo)
                disponible.montant_disponible = mont_dispo
                deblocage.montant_rembourser = remb - ttl_remb


    @api.depends('paiements')
    def _compute_montant_paye(self):
        for rec in self:
            ttl = 0
            paiem = rec.env['credit.operation.paiementdetail'].search([('paiement_global', '=', rec.id)])
            if paiem:
                for p in paiem:
                    ttl += p.montant_paye
            rec.montant_paye = ttl


    @api.depends('ref_opr_deb')
    def _compute_type(self):
        for rec in self:
            rec.type = rec.ref_opr_deb.type

    @api.depends('ref_opr_deb')
    def _compute_ligne_autorisation(self):
        for rec in self:
            rec.ligne_autorisation = rec.ref_opr_deb.ligne_autorisation

    @api.depends('ref_opr_deb')
    def _compute_date_deblocage(self):
        for rec in self:
            rec.date_deblocage = rec.ref_opr_deb.deblocage_date

    @api.depends('ref_opr_deb')
    def _compute_date_echeance(self):
        for rec in self:
            if rec.ref_opr_deb.echeance_date:
                rec.date_echeance = rec.ref_opr_deb.echeance_date
            else:
                rec.date_echeance = rec.ref_opr_deb.deblocage_date

    @api.depends('ref_opr_deb')
    def _compute_montant_echeance(self):
        for rec in self:
            rec.montant_echeance = rec.ref_opr_deb.montant_rembourser

    @api.depends('ref_opr_deb')
    def _compute_dossier_reference(self):
        for rec in self:
            rec.reference_dossier = rec.ref_opr_deb.reference_credit

    @api.depends('ref_opr_deb')
    def _compute_facture(self):
        for rec in self:
            rec.facture = rec.ref_opr_deb.reference_interne

    @api.depends('ref_opr_deb')
    def _compute_fournisseur(self):
        for rec in self:
            rec.fournisseur = rec.ref_opr_deb.partner
    @api.depends('ref_opr_deb')
    def _mise_a_jour(self):
        for rec in self:
            paiements = self.env['credit.operation.p'].search([('ref_opr_deb', '=', rec.ref_opr_deb.id)])
            mont = rec.ref_opr_deb.montant_rembourser - rec.montant_a_rembourser + rec.montant_paye
            print(paiements)
            for p in paiements:
                p.montant_a_rembourser = mont

class Detail_payement(models.Model):
    _name = 'credit.operation.paiementdetail'
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Detail pérations bancaire"

    name = fields.Char(string='Opération detail', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    montant_paye = fields.Float(string="Montant payé", store=True, default=0.00)
    paiement_global = fields.Many2one('credit.operation.p',string='paiement global')
    date_creation = fields.Date(string='Date de paiement', required=True)
    note = fields.Text(string='Description', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('credit.operation.paiementdetail') or _('New')
        result = super(Detail_payement, self).create(vals)
        return result
    def unlink(self):
        for rec in self:
            disponible = rec.env['credit.disponible'].search(
                [('ligne_autorisation', '=', rec.paiement_global.ligne_autorisation.id)])
            deblocage = rec.env['credit.operation.deb'].search([('id', '=', rec.paiement_global.ref_opr_deb.id)])
            recupere = disponible.montant_disponible - rec.montant_paye
            recupere2 = rec.paiement_global.montant_a_rembourser + rec.montant_paye
            cond = rec.paiement_global.echeance
            if cond:
                echeance_partiel = deblocage.env['credit.operation.deb.echeance'].search([('id', '=', cond.id)])
                echeance = rec.env['credit.echeance'].search([('echeance', '=', echeance_partiel.id)])
                echeance_partiel.montant_rembourser = recupere2
                echeance.montant_a_rembourser = recupere2
            else:
                echeance = rec.env['credit.echeance'].search([('ref_opr_deb', '=', rec.paiement_global.ref_opr_deb.id)])
                echeance.montant_a_rembourser = recupere2
            print('bdina supression' + str(disponible.montant_disponible))
            print(recupere)
            disponible.montant_disponible = recupere
            rec.paiement_global.montant_a_rembourser = recupere2
            tmp = deblocage.montant_rembourser
            deblocage.montant_rembourser = tmp + rec.montant_paye
            print(disponible.montant_disponible)
            print(rec.paiement_global.montant_a_rembourser)
        return super(Detail_payement, self).unlink()