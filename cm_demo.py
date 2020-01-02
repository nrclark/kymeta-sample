#!/usr/bin/env python3

""" Example code that exercises customer_management.py """

import customer_management as cm


def main():
    """ Sample routine to read an external file and print a ledger. """

    ledger = cm.Ledger()

    json_data = open('cm_demo.json').read()
    ledger.import_json(json_data)

    print(ledger.generate_report(), end='')


if __name__ == "__main__":
    main()
