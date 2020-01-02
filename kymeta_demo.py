#!/usr/bin/env python3

""" Example code that exercises customer_management.py """

import customer_management as cm
from decimal import Decimal

def main():
    ledger = cm.Ledger()
    ledger.import_json('kymeta_demo.json')

    print(ledger.generate_report(), end='')


if __name__ == "__main__":
    main()
