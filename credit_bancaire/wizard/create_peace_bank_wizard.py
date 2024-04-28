# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CreatePeaceBankWizard(models.TransientModel):
    _name = "peace.wizard"
    _description = "Create Peace Bank Wizard"


    def create_report_peace_bank(self):
        return self.env.ref('credit_bancaire.report_peace_bank_id').report_action(self)
