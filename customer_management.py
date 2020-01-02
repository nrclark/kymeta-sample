#!/usr/bin/env python3

""" Module for customer management. Provides minimal implementation
of customer addition/removal, and of sales addition/removal. """

# pylint: disable=too-few-public-methods

import json
from datetime import datetime
from decimal import Decimal
from enum import Enum


class SaleCode(Enum):
    """ Enumeration of known sale types. Value can be used in report
    generation. """

    UNKNOWN = 'X'
    STANDALONE = 'S'
    UPGRADE = 'U'
    SUBSCRIPTION = 'R'


class CustomerCode(Enum):
    """ Enumeration of known customer types. Value can be used in report
    generation. """

    UNKNOWN = 'X'
    CASH = 'C'
    ACCOUNT = 'A'
    SUBSCRIPTION = 'R'


class BaseSale():
    """ Base-class for sale records. Shouldn't be used standalone. """

    def __init__(self, item, date, price, quantity=1):
        assert isinstance(price, Decimal)

        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        else:
            assert isinstance(date, datetime)

        self.sale_type = SaleCode.UNKNOWN
        self.item = item
        self.date = date
        self.price = price
        self.quantity = quantity

    def __str__(self):
        """ Returns a string representation of the sale. """

        summary = f"{self.item} [{self.sale_type.value}]"
        if self.quantity > 1:
            summary = f"{self.quantity}x {summary}"
        return summary


class ProductSale(BaseSale):
    """ Record-type for standalone/product sales. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sale_type = SaleCode.STANDALONE


class SubscriptionSale(BaseSale):
    """ Record-type for subscription-based sales. """

    def __init__(self, *args, expiration=None, **kwargs):
        super().__init__(*args, **kwargs)

        if expiration:
            if isinstance(expiration, str):
                expiration = datetime.fromisoformat(expiration)
            else:
                assert isinstance(expiration, datetime)

        self.sale_type = SaleCode.SUBSCRIPTION
        self.expiration = expiration

    def __str__(self):
        result = super().__str__()
        if self.expiration:
            result += f" (exp: {self.expiration.strftime('%Y-%m-%d')})"

        return result


class UpgradeSale(BaseSale):
    """ Record-type for upgrade sales to existing customers. """

    def __init__(self, *args, prev_sale=None, **kwargs):
        if prev_sale:
            assert isinstance(prev_sale, BaseSale)

        super().__init__(*args, **kwargs)
        self.sale_type = SaleCode.UPGRADE
        self.prev_sale = prev_sale


class BaseCustomer():
    """ Base-class for customer records. Shouldn't be used standalone. """

    def __init__(self, name, acquisition_date):
        assert isinstance(acquisition_date, datetime)

        self.cust_type = SaleCode.UPGRADE
        self.name = name
        self.acquisition_date = acquisition_date
        self.sales = []

    def add_sale(self, sale):
        """ Adds a sale to customer record. Sale should be of type
        ProductSale, SubscriptionSale, or UpgradeSale. """

        assert isinstance(sale, BaseSale)
        if isinstance(self, CashCustomer):
            assert not isinstance(sale, SubscriptionSale)

        self.sales.append(sale)

    def age(self):
        """ Returns the number of days since customer was acquired. """

        delta = datetime.now() - self.acquisition_date
        return delta.days

    def find_sales(self, datetime_min=None, datetime_max=None):
        """ Finds all sales from a customer in a given timespan. """

        if datetime_min is None:
            datetime_min = datetime.fromtimestamp(0)

        if datetime_max is None:
            datetime_max = datetime.now()

        result = []

        for sale in self.sales:
            if datetime_min <= sale.date <= datetime_max:
                result.append(sale)

        return result

    def summary_line(self):
        """ Returns a single-line summary of customer. Includes approximate
        age of the customer aquisition (in years) and the customer's purchases
        within the last year. """

        age_approx = self.age() / 365
        today = datetime.now()
        last_year = today.replace(year=today.year - 1)

        sale_summaries = []

        for sale in self.find_sales(last_year):
            sale_summaries.append(str(sale))

        result = f"{self.name} [{self.cust_type.value}], "
        result += f"Duration: {age_approx:.1f} years, "
        result += "Purchases in the last year:\n"

        if sale_summaries:
            result += "    " + '\n    '.join(sale_summaries)
        else:
            result += "(none)"

        return result


class CashCustomer(BaseCustomer):
    """ Record-type for customers who make cash/standalone purchases. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cust_type = CustomerCode.CASH


class AccountCustomer(BaseCustomer):
    """ Record-type for customers who are billed by account. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cust_type = CustomerCode.ACCOUNT


class SubscriptionCustomer(BaseCustomer):
    """ Record-type for customers who are billed periodically. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cust_type = CustomerCode.SUBSCRIPTION


SALE_MAP = {
    SaleCode.STANDALONE: ProductSale,
    SaleCode.SUBSCRIPTION: SubscriptionSale,
    SaleCode.UPGRADE: UpgradeSale
}


CUSTOMER_MAP = {
    CustomerCode.SUBSCRIPTION: SubscriptionCustomer,
    CustomerCode.ACCOUNT: AccountCustomer,
    CustomerCode.CASH: CashCustomer
}


class Ledger():
    """ Ledger of customers and their transactions. """

    def __init__(self):
        self.customers = {}

    def add_customer(self, name, acquistion_date, cust_code, cust_id=None):
        """ Adds a new customer to the ledger and returns the customer ID.
        If not supplied, cust_id will default to the customer's name. """

        assert isinstance(cust_code, CustomerCode)

        if isinstance(acquistion_date, str):
            acquistion_date = datetime.fromisoformat(acquistion_date)
        else:
            assert isinstance(acquistion_date, datetime)

        if not cust_id:
            cust_id = name

        if cust_id in self.customers:
            raise ValueError("Customer with this ID already exists")

        customer = CUSTOMER_MAP[cust_code](name, acquistion_date)
        self.customers[cust_id] = customer
        return cust_id

    def add_sale(self, cust_id, sale):
        """ Adds a sale to an existing customer. """

        assert cust_id in self.customers
        self.customers[cust_id].add_sale(sale)

    def customer_list(self):
        """ Returns a list of all customer IDs in the ledger. """

        return [self.customers[x] for x in self.customers]

    def generate_report(self):
        """ Generates a text-based report with a summary of customers and
        their recent purchases. """

        result = "Customers:\n"

        if not self.customers:
            result += "(none)"
        else:
            for customer in self.customer_list():
                result += f"{customer.summary_line()}\n"

        return result

    def import_json(self, filename):
        """ Imports a ledger from a JSON file. """

        file_data = open(filename).read()
        data = json.loads(file_data)
        assert isinstance(data, list)

        for record in data:
            cust_id = record['name']
            cust_code = CustomerCode(record['cust_type'])
            while cust_id in self.customers:
                cust_id += ".alt"

            self.add_customer(record['name'], record['aquisition_date'],
                              cust_code, cust_id)

            for entry in record.get('sales', []):
                price = Decimal(entry['price'])
                sale_gen = SALE_MAP[SaleCode(entry['sale_type'])]
                quantity = entry.get('quantity', 1)

                if 'expiration' in entry:
                    kwargs = {'expiration': entry['expiration']}
                else:
                    kwargs = {}

                sale = sale_gen(entry['item'], entry['date'], price, quantity,
                                **kwargs)

                self.add_sale(cust_id, sale)
