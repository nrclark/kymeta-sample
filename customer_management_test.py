#!/usr/bin/env python3
# pylint: disable=missing-docstring,invalid-name

""" Unit-test suite for customer_mangement module. """

import unittest
import json
import customer_management as cm

ACME_RECORD = """
{
  "name": "Acme, Inc",
  "aquisition_date": "2017-01-02",
  "cust_type": "R",
  "sales": [
    {
      "sale_type": "S",
      "item": "Anvil",
      "date": "2019-04-01",
      "price": "29.99",
      "quantity": 8
    },
    {
      "sale_type": "R",
      "item": "Dynamite",
      "date": "2019-03-20",
      "price": "1.21",
      "quantity": 1,
      "expiration": "2025-03-20"
    },
    {
      "sale_type": "U",
      "item": "Longer Fuse",
      "date": "2019-03-20",
      "price": "0.01",
      "quantity": 1
    }
  ]
}
"""

PYRITE_RECORD = """
{
  "name": "Cash 4 Pyrite",
  "aquisition_date": "1972-01-02",
  "cust_type": "A",
  "sales": [
    {
      "sale_type": "S",
      "item": "Authentic Gold Bricks",
      "date": "2019-04-01",
      "price": "8001.00",
      "quantity": 3
    },
    {
      "sale_type": "U",
      "item": "Software Unlock to Actual Gold",
      "date": "2020-01-01",
      "price": "37.99",
      "quantity": 3
    }
  ]
}
"""

ACME_EXPECTED = """
Acme, Inc [R], Duration: 3.0 years, Purchases in the last year:
    8x Anvil [S]
    Dynamite [R] (exp: 2025-03-20)
    Longer Fuse [U]
"""

PYRITE_EXPECTED = """
Cash 4 Pyrite [A], Duration: 48.0 years, Purchases in the last year:
    3x Authentic Gold Bricks [S]
    3x Software Unlock to Actual Gold [U]
"""


class SanityTest(unittest.TestCase):
    def setUp(self):
        self.sane = True

    def runTest(self):
        self.assertTrue(self.sane)


class ConfirmEmpty(unittest.TestCase):
    def setUp(self):
        self.ledger = cm.Ledger()

    def runTest(self):
        self.assertEqual(len(self.ledger.customers), 0)


class TestImport(unittest.TestCase):
    def setUp(self):
        self.ledger = cm.Ledger()

    def runTest(self):
        self.ledger.import_json(f"[{ACME_RECORD}, {PYRITE_RECORD}]")
        self.assertEqual(len(self.ledger.customers), 2)
        self.assertEqual(len(self.ledger.customers["Acme, Inc"].sales), 3)
        self.assertEqual(len(self.ledger.customers["Cash 4 Pyrite"].sales), 2)


class TestInvalidImport(unittest.TestCase):
    def setUp(self):
        self.ledger = cm.Ledger()

    def runTest(self):
        self.assertRaises(json.decoder.JSONDecodeError, self.invalid_input)

    def invalid_input(self):
        data = "sdlfkjwlerknslkcvnsldkfn1023sd;"
        self.ledger.import_json(data)


class TestPyrite(unittest.TestCase):
    def setUp(self):
        self.ledger = cm.Ledger()
        self.ledger.import_json(f"[{PYRITE_RECORD}]")

    def runTest(self):
        expected = PYRITE_EXPECTED.strip() + "\n"
        self.assertEqual(self.ledger.generate_report(), expected)


class TestAcme(unittest.TestCase):
    def setUp(self):
        self.ledger = cm.Ledger()
        self.ledger.import_json(f"[{ACME_RECORD}]")

    def runTest(self):
        expected = ACME_EXPECTED.strip() + "\n"
        self.assertEqual(self.ledger.generate_report(), expected)


if __name__ == '__main__':
    unittest.main()
