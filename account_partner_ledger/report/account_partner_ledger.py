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
from reportlab.lib.units import mm


class State(object):
    def __init__(self, obj, lines):
        import pdb; pdb.set_trace()
        self.previous = None
        self.lines = lines
        self.iterator = iter(self.lines)
        self.address = "Some address"

def getTextHeight(text, fontName, fontSize, maxWidth, lineHeight):
    """
    Returns the height of a text that should be splitted on 
    multiple lines. It can be used to measure the height of a 
    cell in a table.
    """
    lines = simpleSplit(text, fontName, fontSize, maxWidth)
    return len(lines) * lineHeight

def iter_current_lines(state, container, iterable, max_step):
    """
    Iters over the quantity of lines that fit within the
    table for one page.

    When there is not enough space, it will raise a StopIteration
    error to communicate that it should stop getting lines for
    the current page.

    The iterable will be used as long as there are lines. This make
    it possible to split the lines over multiple pages.
    """
    balance = state.previous['total'] if state.previous else 0

    height = 0
    max_width = 73

    line_height = 5
    max_height = 100

    line_width = (max_width - 10) * mm
    font_size = 3.5 * mm

    while height < max_height:
        try:
            value = next(iterable)
            credit = value if int(height) % 2 == 0 else 0
            debit = value if int(height+1) % 2 == 0 else 0

            from random import randrange

            #description = "a"
            #description = " ".join([str(a) for a in range(10)]) * 4
            description = "Abcdef (ABC) abcd" * randrange(1, 3)
            description += "abcdef a dfdf" * randrange(1, 4)

            height += getTextHeight(description,
                                    "Helvetica",
                                    font_size,
                                    line_width,
                                    line_height)

            balance += debit - credit

            val = {
                "payments": credit,
                "charges": debit,
                "date": "10-17-12",
                "ref": "00011336",
                "description": description,
                "balance": balance
            }

            container["total"] = balance
            container["lines"].append(val)

        except StopIteration:
            container["not_last"] = False
            break


def PageIterator(partner, lines):
    """
    Split a set of lines on multiple pages. It use the
    line_iterator to iterate over lines that fit within
    a defined height.
    """

    state = State(partner, lines)
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
    """
    Returns an image as base64 that can be used inside rml
    templates.
    """
    file = open("/usr/share/icons/hicolor/64x64/apps/skype.png")
    return base64.encodestring(file.read())

def get_pages(partner, lines):
    return PageIterator(partner, lines)

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
