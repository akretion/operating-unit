# Copyright 2026 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains("journal_id", "analytic_account_id")
    def _check_analytic_account(self):
        for record in self:
            if record.analytic_account_id and (
                record.journal_id.operating_unit_id
                != record.analytic_account_id.operating_unit_id
            ):
                raise ValidationError(_(
                    "Le compte analytic doit appartenir à la même Opérating Unit"
                    "que celle du journal"
                    ))
