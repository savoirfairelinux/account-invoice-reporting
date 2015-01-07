# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.report import report_sxw
from account.report.account_partner_ledger import third_party_ledger

from datetime import date
import base64
from reportlab.platypus.flowables import Image
from reportlab.lib.utils import simpleSplit 


class State(object):
    def __init__(self, obj):
        self.previous = None
        self.lines = [i for i in range(25)]
        self.iterator = iter(self.lines)
        self.address = "Some address"


def iter_current_lines(state, container, iterable, max_step):
    balance = state.previous['total'] if state.previous else 0

    for i in range(max_step):
        try:
            value = next(iterable)
            credit = value if i % 2 == 0 else 0
            debit = value if (i+1) % 2 == 0 else 0

            balance += debit - credit

            val = {
                "payments": credit,
                "charges": debit,
                "date": "10-17-12",
                "ref": "00011336",
                "description": "Abcdef (ABC) abcdef abcdefg df Traghpert fg",
                "balance": balance
            }

            container["total"] += balance
            container["lines"].append(val)
        except StopIteration:
            container["not_last"] = False
            break


def PageIterator(obj):
    state = State(obj)
    counter = 1

    while True:
        if not state.previous:
            last_total = 1
        else:
            last_total = state.previous["total"]

        current = {
            "index": counter,
            "period_start": "01-10-13",
            "period_end": "19-23-14",
            "address": state.address,
            "previous": last_total,
            "total": last_total,
            "not_last": True,
            "lines": []
        }

        counter += 1

        iter_current_lines(state, current, state.iterator, 5)

        if len(current["lines"]) == 0:
            state.previous["not_last"] = False
            current = None
            yield state.previous
            raise StopIteration()

        if state.previous:
            yield state.previous

        state.previous = current

def format_date(date):
    """
    Format a date or datetime object to the day-month-year
    format with two digits.

    >> format_date(date(2015, 1, 7))
    "07-01-15"
    >> format_date(date(2020, 4, 10))
    "10-04-20"
    """
    return date.strftime("%d-%m-%y")

def get_today_date():
    """
    Get current date formatted to string.
    """
    return format_date(date.today())

def get_image():
    file = open("/usr/share/icons/hicolor/64x64/apps/skype.png")
    return base64.encodestring(file.read())

def get_pages(obj, count):
    return PageIterator(count)

class account_partner_ledger(third_party_ledger):
    def __init__(self, cr, uid, name, context=None):
        base_class = super(account_partner_ledger, self)
        base_class.__init__(cr, uid, name, context=context)

        self.localcontext.update({
            "range": range,
            "get_pages": get_pages,
            "get_image": get_image,
            "format_date": format_date,
            "get_today_date": get_today_date,
        })

report_sxw.report_sxw(
    'report.account_partner_ledger.account_partner_ledger',
    'res.partner',
    'addons/account_partner_ledger/report/account_partner_ledger.rml',
    parser=account_partner_ledger,
    header=False
)
