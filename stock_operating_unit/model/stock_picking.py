# © 2019 ForgeFlow S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    operating_unit_id = fields.Many2one(
        "operating.unit",
        "Requesting Operating Unit",
        related="picking_type_id.warehouse_id.operating_unit_id",
        store=True,
    )
