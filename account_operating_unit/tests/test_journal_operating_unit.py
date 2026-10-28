# © 2019 ForgeFlow S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import odoo.tests

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestJournalOperatingUnit(AccountTestInvoicingCommon):
    """A move created without operating unit takes the one of its journal.

    The journal may be given in the values, come from the context or be the
    default one of the journal field: in the three cases the operating unit has
    to end up on the move and on its lines. Journal entries are covered as well
    as invoices, and a journal without operating unit leaves the move free for a
    manual value.
    """

    def setUp(self):
        super().setUp()
        self.company = self.env.user.company_id
        self.move_model = self.env["account.move"]
        self.journal_model = self.env["account.journal"]
        self.ou1 = self.env.ref("operating_unit.main_operating_unit")
        self.b2b = self.env.ref("operating_unit.b2b_operating_unit")
        self.b2c = self.env.ref("operating_unit.b2c_operating_unit")
        main_company = self.env.ref("base.main_company")
        # the demo operating units belong to the main company: give the user
        # access to both companies to be able to move them on its own one
        self.env.user.write(
            {
                "company_ids": [(4, main_company.id), (4, self.company.id)],
                "operating_unit_ids": [(4, self.b2b.id), (4, self.b2c.id)],
            }
        )
        (self.ou1 + self.b2b + self.b2c).write({"company_id": self.company.id})
        self.account = self.company_data["default_account_expense"]

    def _create_journal(self, journal_type, code, operating_unit=None):
        vals = {
            "name": "Journal %s - Test" % code,
            "code": code,
            "type": journal_type,
            "company_id": self.company.id,
        }
        if operating_unit:
            vals["operating_unit_id"] = operating_unit.id
        return self.journal_model.create(vals)

    def _prepare_entry_vals(self, **kwargs):
        lines = [
            {
                "name": "Debit",
                "account_id": self.account.id,
                "debit": 100.0,
                "credit": 0.0,
            },
            {
                "name": "Credit",
                "account_id": self.account.id,
                "debit": 0.0,
                "credit": 100.0,
            },
        ]
        vals = {"line_ids": [(0, 0, line) for line in lines]}
        vals.update(kwargs)
        return vals

    def _prepare_invoice_vals(self, **kwargs):
        vals = {
            "partner_id": self.partner_a.id,
            "move_type": "in_invoice",
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product_a.id,
                        "quantity": 1.0,
                        "price_unit": 100.0,
                    },
                )
            ],
        }
        vals.update(kwargs)
        return vals

    def _assert_operating_unit(self, move, operating_unit):
        self.assertEqual(len(move.line_ids), 2)
        self.assertEqual(move.operating_unit_id, operating_unit)
        self.assertEqual(move.line_ids.operating_unit_id, operating_unit)

    def test_invoice_operating_unit_from_explicit_journal(self):
        journal = self._create_journal("purchase", "TJI01", self.b2b)
        invoice = self.move_model.with_context(default_move_type="in_invoice").create(
            self._prepare_invoice_vals(journal_id=journal.id)
        )
        self.assertEqual(invoice.journal_id, journal)
        self._assert_operating_unit(invoice, self.b2b)

    def test_invoice_operating_unit_from_context_journal(self):
        journal = self._create_journal("purchase", "TJI02", self.b2c)
        invoice = self.move_model.with_context(
            default_move_type="in_invoice", default_journal_id=journal.id
        ).create(self._prepare_invoice_vals())
        self.assertEqual(invoice.journal_id, journal)
        self._assert_operating_unit(invoice, self.b2c)

    def test_invoice_operating_unit_from_default_journal(self):
        """Neither journal nor operating unit in the values nor in the context,
        as when a bill is generated from a purchase order."""
        ctx = {"default_move_type": "in_invoice"}
        journal = self.move_model.with_context(**ctx)._get_default_journal()
        journal.operating_unit_id = self.b2b
        invoice = self.move_model.with_context(**ctx).create(
            self._prepare_invoice_vals()
        )
        self.assertEqual(invoice.journal_id, journal)
        self._assert_operating_unit(invoice, self.b2b)

    def test_entry_operating_unit_from_explicit_journal(self):
        journal = self._create_journal("general", "TJE01", self.b2c)
        entry = self.move_model.create(self._prepare_entry_vals(journal_id=journal.id))
        self.assertEqual(entry.journal_id, journal)
        self._assert_operating_unit(entry, self.b2c)

    def test_entry_operating_unit_from_context_journal(self):
        journal = self._create_journal("general", "TJE02", self.b2b)
        entry = self.move_model.with_context(default_journal_id=journal.id).create(
            self._prepare_entry_vals()
        )
        self.assertEqual(entry.journal_id, journal)
        self._assert_operating_unit(entry, self.b2b)

    def test_entry_without_journal_operating_unit_is_settable(self):
        """A journal without operating unit leaves the field empty, and a value
        set afterwards is propagated to the lines."""
        journal = self._create_journal("general", "TJE03")
        entry = self.move_model.create(self._prepare_entry_vals(journal_id=journal.id))
        self.assertFalse(entry.operating_unit_id)
        self.assertFalse(entry.line_ids.operating_unit_id)
        entry.operating_unit_id = self.ou1
        self._assert_operating_unit(entry, self.ou1)

    def test_explicit_operating_unit_wins_over_journal(self):
        journal = self._create_journal("general", "TJE04", self.b2b)
        entry = self.move_model.create(
            self._prepare_entry_vals(
                journal_id=journal.id, operating_unit_id=self.b2c.id
            )
        )
        self.assertEqual(entry.journal_id, journal)
        self._assert_operating_unit(entry, self.b2c)
