# Copyright 2016-17 ForgeFlow S.L.
# Copyright 2016-17 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        string="Operating Units",
    )
