
from odoo import models, fields, api,_
import datetime


class TaxSmcp(models.Model):
    _name = "smcp.smcp"

    name=fields.Char(string="Espèce")
    prix_base= fields.Float(string="Prix de base")
    currency_id = fields.Many2one('res.currency', string="Devise")
    taux = fields.Float(string="Taux")
    smcp_tax = fields.One2many('lingtax.lingtax', 'smcp_id', string="Taxes SMCP")


class LignesVentesTaxesSmcp(models.Model):
    _name="lingtax.lingtax"

    qty = fields.Float(string="Quantité")
    price_base = fields.Float(string="Prix de base")
    order_id = fields.Many2one('sale.order', string="Bon de commande")
    name = fields.Char(string="Espèce", related="smcp_id.name")
    sale_order_line_id = fields.Many2one('sale.order.line', string="Ligne de vente")
    taux = fields.Float(string="Taux")
    total = fields.Float(string="Montant")
    currency_id = fields.Many2one('res.currency', string="Devise")
    smcp_id = fields.Many2one('smcp.smcp', string="Tax SMCP")

    @api.depends('qty', 'price_base', 'taux')
    def _calcule_montant(self):
        for record in self:
            record[("total")] = record.qty * record.price_base * record.taux / 100

