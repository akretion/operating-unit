# © 2019 ForgeFlow S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("operating_unit_id") and vals.get("move_id"):
                move = self.env["account.move"].browse(vals["move_id"])
                if move.operating_unit_id:
                    vals["operating_unit_id"] = move.operating_unit_id.id
        return super().create(vals_list)


class AccountMove(models.Model):
    _inherit = "account.move"

    operating_unit_id = fields.Many2one(comodel_name="operating.unit")

    @api.onchange("journal_id")
    def _onchange_journal_operating_unit(self):
        for move in self:
            if move.journal_id.operating_unit_id:
                move.operating_unit_id = move.journal_id.operating_unit_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("operating_unit_id") and vals.get("journal_id"):
                journal = self.env["account.journal"].browse(vals["journal_id"])
                if journal.operating_unit_id:
                    vals["operating_unit_id"] = journal.operating_unit_id.id
        return super().create(vals_list)

    def write(self, vals):
        if "operating_unit_id" in vals:
            lines_to_update = {
                move.id: move.line_ids.filtered(
                    lambda l: l.operating_unit_id == move.operating_unit_id
                )
                for move in self
            }
        res = super().write(vals)
        if "operating_unit_id" in vals:
            for move in self:
                lines_to_update[move.id].write(
                    {"operating_unit_id": vals["operating_unit_id"]}
                )
        return res
