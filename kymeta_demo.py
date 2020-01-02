#!/usr/bin/env python3

""" Module for customer management. Provides minimal implementation
of customer addition/removal, and of sales addition/removal. """

import customer_management as cm
from decimal import Decimal

def main():
    ledger = cm.Ledger()

    acme = ledger.add_customer("Acme Inc.", "1984-01-02", 
                               cm.CustomerCode.SUBSCRIPTION)

    anvil_sale = cm.ProductSale("Anvil", "2019-04-01", Decimal("29.99"), 8)
    anvil_sale = cm.ProductSale("Anvil", "2019-04-01", Decimal("29.99"), 8)
    ledger.add_sale(acme, anvil_sale)

    print(ledger.generate_report(), end='')


if __name__ == "__main__":
    main()
