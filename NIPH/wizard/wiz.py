from odoo import models, fields, api


class wiz_calc_taux(models.TransientModel):
    _name = 'calc.taux.wiz'

    new_rate = fields.Float(required=True, string="Taux SMCP")

    def rate_update(self):
        smcp_ids = self.env['smcp.smcp'].search([])
        for rate in smcp_ids:
            rate.taux = self.new_rate
