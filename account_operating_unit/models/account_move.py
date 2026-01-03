# © 2019 ForgeFlow S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    operating_unit_id = fields.Many2one(
        related="move_id.operating_unit_id",
        store=True,
    )

    @api.constrains("journal_id", "analytic_account_id")
    def _check_analytic_account(self):
        for record in self:
            if record.analytic_account_id.operating_unit_id and (
                record.journal_id.operating_unit_id
                != record.analytic_account_id.operating_unit_id
            ):
                raise ValidationError(
                    _(
                        "Le compte analytic doit appartenir à la même Unité Opérationnel"
                        "que celle du journal"
                    )
                )


class AccountMove(models.Model):
    _inherit = "account.move"

    operating_unit_id = fields.Many2one(
        related="journal_id.operating_unit_id",
        store=True,
    )
