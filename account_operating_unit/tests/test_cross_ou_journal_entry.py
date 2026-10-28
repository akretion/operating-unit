# © 2019 ForgeFlow S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import odoo.tests

from . import test_account_operating_unit as test_ou


@odoo.tests.tagged("post_install", "-at_install")
class TestCrossOuJournalEntry(test_ou.TestAccountOperatingUnit):
    def test_cross_ou_journal_entry(self):
        """An entry mixing several operating units keeps, on each line, the
        operating unit it was given with.

        The cross operating unit clearing entries that used to be generated at
        posting are gone: a line is no longer forced to the operating unit of
        its journal, so its own operating unit survives the posting.
        """
        self.acc_move_model = self.env["account.move"]
        journal = self.journal_model.search(
            [("code", "=", "MISC"), ("company_id", "=", self.company.id)], limit=1
        )
        lines = [
            (
                0,
                0,
                {
                    "name": "Test",
                    "account_id": self.current_asset_account_id.id,
                    "debit": 0,
                    "credit": 100,
                    "operating_unit_id": self.b2b.id,
                },
            ),
            (
                0,
                0,
                {
                    "name": "Test",
                    "account_id": self.current_asset_account_id.id,
                    "debit": 100,
                    "credit": 0,
                    "operating_unit_id": self.b2c.id,
                },
            ),
        ]
        # get default values of account move
        move_vals = self.acc_move_model.default_get([])
        move_vals.update({"journal_id": journal.id, "line_ids": lines})
        move = self.acc_move_model.with_user(self.user_id.id).create(move_vals)
        self.assertEqual(move.line_ids.operating_unit_id, self.b2b | self.b2c)
        move.action_post()
        # no clearing line has been added at posting
        self.assertEqual(len(move.line_ids), 2)
        self.assertEqual(move.line_ids.operating_unit_id, self.b2b | self.b2c)
