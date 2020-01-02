#!/usr/bin/env python3

""" Example code that exercises customer_management.py """

import customer_management as cm
from decimal import Decimal

def main():
    ledger = cm.Ledger()

    json_data =  open('kymeta_demo.json').read()
    ledger.import_json(json_data)

    print(ledger.generate_report(), end='')


if __name__ == "__main__":
    main()
