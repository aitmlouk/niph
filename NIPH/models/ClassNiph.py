
from odoo import models, fields, api,_
import datetime


class Partner(models.Model):
    _inherit = 'res.partner'

    supplier_ok = fields.Boolean(string='Fournisseur par défaut poisson')
    part_ids = fields.One2many("ligne.interm", "partner_id", string="Intermédiaire")


class Container(models.Model):
    _name = "cont.cont"

    tail_container = fields.Char(string="Container")
    container = fields.One2many("product.supplierinfo", "container_id", string="Container")


class Destinations(models.Model):
     _name = "dest.dest"

     name = fields.Char(string="Nom")
     destination_id = fields.One2many("product.supplierinfo", "destination_id", string="Destination")


class Produit(models.Model):
    _inherit = 'product.supplierinfo'

    container_id = fields.Many2one("cont.cont", string="Container")
    destination_id = fields.Many2one("dest.dest", string="Destination")
    standard = fields.Boolean(string="Fournisseur standard")


class CompteTax(models.Model):
    _inherit = "account.tax"

    ex_tva_achats = fields.Boolean(string="Exonéré de TVA – Achats")
    ex_tva_ventes = fields.Boolean(string="Exonéré de TVA – Ventes")


class ProductT(models.Model):
    _inherit = 'product.template'

    codevise = fields.Float(string="Coût pour devis")
    espece = fields.Char(string="Espèce")
    espece_id = fields.Many2one('smcp.smcp', string="Espéce")
    type_produit = fields.Selection([('export', 'Prestation liée à l\'export'), ('port', 'Frais de transport'),
                                     ('file', 'Frais de dossier transport'),
                                     ('inter', 'Article pour commission intermédiaire'),
                                     ('freight', 'Freight maritime')])


class ArticlP(models.Model):
    _inherit = 'product.product'

    espece = fields.Char(string="Espèce")
    espece_id = fields.Many2one('smcp.smcp', string="Espèce")
    type_produit = fields.Selection([('export', 'Prestation liée à l\'export'), ('port', 'Frais de transport'), ('file', 'Frais de dossier transport'),('inter', 'Article pour commission intermédiaire'),('freight', 'Freight maritime')])
    prod_ids = fields.One2many("ligne.interm", "product_id", string="Produit")
    pr_ids = fields.One2many("gestion.marge", "product_id", string="Produit")


class TaxSmcp(models.Model):
    _name = "smcp.smcp"

    name=fields.Char(string="Espèce")
    prix_base= fields.Float(string="Prix de base")
    currency_id = fields.Many2one('res.currency', string="Devise")
    taux = fields.Float(string="Taux")
    smcp_tax = fields.One2many('lingtax.lingtax', 'smcp_id', string="Taxes SMCP")


class SmcpCurrency(models.Model):
    _inherit='res.currency'

    taxsmcp = fields.One2many("smcp.smcp", "currency_id", string="Device")
    devis_ids = fields.One2many("lingtax.lingtax", "currency_id", string="Device")
    inter_ids = fields.One2many("ligne.interm", "currency_id", string="Device")
    currency_ids = fields.One2many("gestion.marge", "devise", string="Device")


class DemandePrix(models.Model):
    _inherit = 'purchase.order'

    sale_id = fields.Many2one("sale.order", string="Vente")
    client = fields.One2many("sale.order", "partner_id", string="Client")
    transport = fields.Boolean(string="Transport")
    prestation = fields.Boolean(string="Prestation")
    poissons = fields.Boolean(string="Poissons")


class PurchaseOrderLine(models.Model):
    _inherit="sale.order.line"


class Salesale(models.Model):
    _inherit = 'sale.order'

    vente_ids = fields.One2many("purchase.order", "sale_id", string="Vente")
    sale_order_ids = fields.One2many("ventcout.ventcout", "order_id", string="Bon de commande")
    linge_tax_ids = fields.One2many("lingtax.lingtax", "order_id", string="Bon de commande")
    vent_ids = fields.One2many("ligne.interm", "sale_id", string="Vente")
    frais_port = fields.Boolean(string="Avec frais de port")
    avec_present = fields.Boolean(string="Avec prestation")
    destination_id = fields.Many2one("dest.dest", string="Destination")
    currency_id = fields.Many2one("res.currency", related='pricelist_id.company_id.currency_id', string="Currency", required=False)
    currency_id_pricelist = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency pricelist")
    container_id = fields.Many2one("cont.cont", string="Container")
    change_rate = fields.Float(string="Taux de change")
    sale_inter_ids = fields.One2many("sale.inter.order.line", 'sale_ord_id', string="Intermédiaires vente")
    purchase_fish_ids = fields.One2many("purchase.order.line", 'purchase_order_id',
                                        domain=[('order_id.poissons', '=', True)],
                                        string="Intermédiaires achat")


class saleInterOrderLine(models.Model):
    _name = 'sale.inter.order.line'

    name = fields.Char(string="Nom")
    partner_id = fields.Many2one('res.partner', string="Intermédiaires")
    product_id = fields.Many2one('product.product', string="Produit")
    amount = fields.Monetary(string="Montant")
    currency_id = fields.Many2one('res.currency', string="Devis")
    qty = fields.Float(string="Qty")
    total = fields.Float(string="Total")
    sale_ord_id = fields.Many2one('sale.order', string="Command")
    sale_line_id = fields.Many2one('sale.order.line', string="Ligne command")

    @api.onchange('product_id', 'qty', 'amount')
    def compute_total(self):
        self.amount = self.product_id.lst_price
        self.total = self.qty * self.amount

    @api.model
    def create(self, values):
        res = super(saleInterOrderLine, self).create(values)
        a = self.env['sale.order.line'].search(
            [('order_id', '=', res.sale_ord_id.id), ('product_id', '=', res.product_id.id)], limit=1)
        res.sale_line_id = a.id
        res.currency_id = a.currency_id.id

        return res


class LinOrder(models.Model):
    _inherit = "sale.order.line"

    order_ids = fields.One2many("lingtax.lingtax", "sale_order_line_id", string="Ligne de vente")
    sl_ids = fields.One2many("ligne.interm", "sale_line_id", string="Ligne de vente")
    commission = fields.Monetary(string='Commission', compute='compute_commission', readonly=True)

    @api.depends('product_uom_qty', 'product_id')
    def compute_commission(self):
        for record in self:
            sale_interme_ids = self.env['sale.inter.order.line'].search([('sale_line_id', '=', record.id)])
            commission = 0.0
            for line in sale_interme_ids:
                commission += line.qty * line.amount
            print('-----', commission)
            record.commission = commission / record.product_uom_qty


    @api.model
    def create(self, values):
        res = super(LinOrder, self).create(values)
        a = self.env['sale.inter.order.line'].search(
            [('sale_ord_id', '=', res.order_id.id), ('product_id', '=', res.product_id.id)])
        for line in a:
            line.write({
                'sale_line_id': res.id,
                'currency_id': res.currency_id.id
            })
        print('---------', a)
        if res.order_id.pricelist_id.currency_id.id != res.company_id.currency_id.id:
            print('---------', 'OK')
            a = self.env['res.partner'].search([('supplier_ok', '!=', False)], limit=1)
            purch = self.env['purchase.order'].search([('poissons', '!=', False), ('sale_id', '=', res.order_id.id)])
            if len(purch) == 0:
                reference = self.env['ir.sequence'].next_by_code('purchase.order')
                self.env['purchase.order'].create({
                    'partner_id': a.id,
                    'sale_id': res.order_id.id,
                    'name': reference,
                    'poissons': True,

                })
            order = self.env['purchase.order'].search([('sale_id', '=', res.order_id.id), ('poissons', '!=', False)],
                                                 limit=1)
            b = self.env['account.tax'].search([('ex_tva_ventes', '!=', False)], limit=1)
            self.env['purchase.order.line'].create({
                'product_id': res.product_id.id,
                'partner_id': a.id,
                'company_id': 1,
                'name': res.name,
                'order_id': order.id,
                'product_qty': res.product_uom_qty,
                'product_uom': res.product_uom.id,
                'sale_line_id': res.id,
                'price_unit': res.product_id.codevise,
                'taxes_id': [[4, b.id]],
                'date_planned': order.date_order + + datetime.timedelta(days=1),
            })

        return res

    def write(self, values):
        res = super(LinOrder, self).write(values)
        a = self.env['sale.inter.order.line'].search(
            [('sale_ord_id', '=', self.order_id.id), ('product_id', '=', self.product_id.id)])
        for line in a:
            line.write({
                'sale_line_id': self.id,
                'currency_id': self.currency_id.id
            })
        return res


class CoutFix(models.Model):
    _name = 'coutfix.coutfix'

    name = fields.Char(string="Nom")
    montant = fields.Float(string="Montant/tonne")
    fix_cost = fields.One2many('ventcout.ventcout', 'fix_id', string="cout fixe")


class VentCoutFix(models.Model):
    _name = 'ventcout.ventcout'

    fix_id = fields.Many2one('coutfix.coutfix', string="cout fixe")
    total = fields.Float(string="Total")
    qty = fields.Float(string="Quantité")
    amount = fields.Float(string="Montant")
    order_id = fields.Many2one('sale.order', string="Bon de comande")


    @api.depends('qty','amount')
    def _calcule_total(self):
        for record in self:
            record[("total")] = record.qty * record.amount


class LignesVentesTaxesSmcp(models.Model):
    _name="lingtax.lingtax"

    qty = fields.Float(string="Quantité", related="sale_order_line_id.product_uom_qty")
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


class LigneInterm(models.Model):
    _name = 'ligne.interm'

    @api.depends('qty', 'amount')
    def _calc_total(self):
        for record in self:
            record[("total")] = record.qty * record.amount

    partner_id = fields.Many2one('res.partner', string="Intermédiaire")
    currency_id = fields.Many2one('res.currency', string="Devise")
    total = fields.Float(string="Total")
    sale_line_id = fields.Many2one('sale.order.line', string="Ligne de vente")
    amount = fields.Float(string="Montant/tonne")
    qty = fields.Float(string="Quantité", related="sale_line_id.product_uom_qty")
    product_id = fields.Many2one('product.product', string="Produit")
    sale_id = fields.Many2one('sale.order', string="Vente")


class GestMarg(models.Model):
    _name = 'gestion.marge'

    devise = fields.Many2one('res.currency', string="Devise")
    marge = fields.Float(string="Marge")
    unity = fields.Char(readOnly=True, string="Unité de mesure", related="product_id.uom_id.name")
    product_id = fields.Many2one('product.product', string="Produit")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_inter_ids = fields.One2many("purchase.inter.order.line", 'purchase_ord_id', string="Intermédiaires achat")
    purchase_fish_ids = fields.One2many("purchase.order.line", 'purchase_ord', domain=[('order_id.poissons', '=', True)],
                                        string="Intermédiaires achat")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_ord = fields.Many2one('purchase.order', string="Achats poissons")
    purchase_order_id = fields.Many2one('sale.order', string="Vente poissons")


class PurshaseOrderInter(models.Model):
    _name = 'purchase.inter.order.line'

    name = fields.Char(string="Nom")
    partner_id = fields.Many2one('res.partner', string="Intermédiaires")
    product_id = fields.Many2one('product.product', string="Produit")
    amount = fields.Monetary(string="Montant")
    currency_id = fields.Many2one('res.currency', string="Devis")
    qty = fields.Float(string="Qty")
    total = fields.Float(string="Total")
    purchase_ord_id = fields.Many2one('purchase.order', string="Command achat")
    sale_id = fields.Many2one('sale.order', string="Vente")

    @api.onchange('product_id', 'qty', 'amount')
    def compute_total(self):
        self.amount = self.product_id.lst_price
        self.total = self.qty * self.amount

    @api.model
    def create(self, values):
        res = super(PurshaseOrderInter, self).create(values)
        res.sale_id = res.purchase_ord_id.sale_id.id
        a = self.env['purchase.order.line'].search(
            [('order_id', '=', res.purchase_ord_id.id), ('product_id', '=', res.product_id.id)], limit=1)
        qt = sum(a.mapped('product_qty'))
        res.qty = qt
        return res