# © 2019 ForgeFlow S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    operating_unit_id = fields.Many2one(
        related="move_id.operating_unit_id",
        store=True,
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    operating_unit_id = fields.Many2one(
        related="journal_id.operating_unit_id",
        store=True,
    )
