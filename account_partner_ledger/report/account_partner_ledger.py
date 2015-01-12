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

from datetime import datetime, date, timedelta

from reportlab.lib.utils import simpleSplit
from reportlab.lib.units import mm


def get_month(current):
    return datetime(current.year, current.month, 1)


def get_previous_month(current):
    current_month = get_month(current)
    return get_month(current_month - timedelta(days=5))


class State(object):
    def __init__(
            self, obj, lines, max_width, max_height,
            font_size=3.5, line_height=5, font_name="Helvetica",
            date_from=None, date_to=None
            ):
        self.previous = None
        self.lines = lines
        self.iterator = iter(self.lines)
        self.date_from = date_from
        self.date_to = date_to

        # Control container filling
        self.max_width = max_width
        self.font_name = font_name
        self.font_size = font_size
        self.line_height = line_height
        self.max_height = max_height

        self.periods = []

        if not date_to:
            current = datetime.now()
        else:
            current = date_to

        month = timedelta(days=30)

        self.periods.append({
            "label": "CURRENT",
            "value": 0
        })
        self.periods.append({
            "label": (current - month).strftime("%b"),
            "value": 0
        })
        self.periods.append({
            "label": (current - month - month).strftime("%b"),
            "value": 0
        })
        self.periods.append({
            "label": "Pre-%s" % ((current - month - month).strftime("%b")),
            "value": 0
        })

    def compute_periods(self, report, partner):
        day = timedelta(days=1)
        date11 = get_month(self.date_to)
        date12 = self.date_to
        date21 = get_previous_month(date11)
        date22 = date11 - day
        date31 = get_previous_month(date21)
        date32 = date22 - day
        date41 = datetime(1970, 1, 1)
        date42 = date32 - day

        balance1 = report.get_balance(partner, date11, date12)[0][2]
        balance2 = report.get_balance(partner, date21, date22)[0][2]
        balance3 = report.get_balance(partner, date31, date32)[0][2]
        balance4 = report.get_balance(partner, date41, date42)[0][2]

        self.periods[0]['value'] = balance1
        self.periods[1]['value'] = balance2
        self.periods[2]['value'] = balance3
        self.periods[3]['value'] = balance4


def getTextHeight(text, fontName, fontSize, maxWidth, lineHeight):
    """
    Returns the height of a text that should be splitted on
    multiple lines. It can be used to measure the height of a
    cell in a table.
    """
    lines = simpleSplit(text, fontName, fontSize, maxWidth)
    return len(lines) * lineHeight


def erpdate_to_datetime(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


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

    line_width = (state.max_width - 10) * mm
    font_size = state.font_size * mm

    while height < state.max_height:
        try:
            value = next(iterable)
            credit = value['credit']
            debit = value['debit']
            ref = value['ref'] or value['a_code']
            description = value['name'] or value['a_name']
            move_date = erpdate_to_datetime(value['date'])

            # from random import randrange
            # description = "a"
            # description = " ".join([str(a) for a in range(10)]) * 4
            # description = "Abcdef (ABC) abcd" * randrange(1, 3)
            # description += "abcdef a dfdf" * randrange(1, 4)

            height += getTextHeight(description,
                                    state.font_name,
                                    font_size,
                                    line_width,
                                    state.line_height)

            balance += debit
            balance -= credit

            val = {
                "payments": credit,
                "charges": debit,
                "date": move_date,
                "ref": ref,
                "description": description,
                "balance": balance
            }

            container["total"] = balance
            container["lines"].append(val)

        except StopIteration:
            container["not_last"] = False
            break


def PageIterator(report, partner, lines, max_width, max_height, font_size):
    """
    Split a set of lines on multiple pages. It use the
    line_iterator to iterate over lines that fit within
    a defined height.
    """

    date_from = report._get_start(report.data)
    date_to = report._get_end(report.data)
    state = State(partner, lines, max_width, max_height, font_size,
                  date_from=date_from, date_to=date_to)
    counter = 1
    old_date = datetime(1970, 01, 01)

    while True:

        if not state.previous:
            last_total = report.get_balance(partner, old_date, date_from)[0][2]
        else:
            last_total = state.previous["total"]

        current = {
            "index": counter,
            "period_start": date_from,
            "period_end": date_to,
            "previous": last_total,
            "total": last_total,
            "not_last": True,
            "lines": [],
            "periods": state.periods,
        }

        counter += 1

        iter_current_lines(state, current, state.iterator, 5)

        if len(current["lines"]) == 0:
            state.previous["not_last"] = False
            current = None
            state.compute_periods(report, partner)
            yield state.previous
            raise StopIteration()

        if state.previous:
            yield state.previous

        state.previous = current

reports = {
    "report": "%d-%m-%y",
    "erp": "%Y-%m-%d",
}


def format_date(date, format_name="report"):
    """
    Format a date or datetime object to the day-month-year
    format with two digits.

    >> format_date(date(2015, 1, 7))
    "07-01-15"
    >> format_date(date(2020, 4, 10))
    "10-04-20"
    """

    return date.strftime(reports[format_name])


def get_today_date():
    """
    Get current date formatted to string.
    """
    return format_date(date.today())


class account_partner_ledger(third_party_ledger):
    def __init__(self, cr, uid, name, context=None):
        base_class = super(account_partner_ledger, self)
        base_class.__init__(cr, uid, name, context=context)

        self.localcontext.update({
            "range": range,
            "get_pages": self._get_pages,
            "format_date": format_date,
            "get_today_date": get_today_date,
            "get_end": self._get_end,
            "get_start": self._get_start,
        })

    def set_context(self, objects, data, ids, report_type=None):
        base_class = super(account_partner_ledger, self)
        base_class.set_context(objects, data, ids, report_type)
        self.data = data

    def _get_pages(self, partner, lines, max_width, max_height, font_size):
        return PageIterator(self, partner, lines,
                            max_width, max_height, font_size)

    def _get_start(self, data):
        form = data['form']

        if form['filter'] == 'filter_no':
            # 90 days in the past (3 months)
            date_from = date.today() - timedelta(days=90)
            return date_from
        elif form['filter'] == 'filter_date':
            date_str = form['date_from']
        elif form['filter'] == 'filter_period':
            date_str = form['period_from']

        if date_str:
            return erpdate_to_datetime(date_str)

    def _get_end(self, data):
        form = data['form']

        if form['filter'] == 'filter_no':
            date_from = date.today()
            return date_from
        elif form['filter'] == 'filter_date':
            date_str = form['date_to']
        elif form['filter'] == 'filter_period':
            date_str = form['period_to']

        if date_str:
            return erpdate_to_datetime(date_str)

    def get_balance(self, partner, date_from, date_to):
        move_state = ['draft', 'posted']

        if self.target_move == 'posted':
            move_state = ['posted']
        if self.reconcil:
            RECONCILE_TAG = " "
        else:
            RECONCILE_TAG = "AND l.reconcile_id IS NULL"

        obj_move = self.pool.get('account.move.line')

        ctx = self.data['form'].get('used_context', {}).copy()
        ctx['date_from'] = format_date(date_from, 'erp')
        ctx['date_to'] = format_date(date_to, 'erp')

        query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)

        self.cr.execute(
            (
                "SELECT COALESCE(SUM(l.debit),0.0),"
                " COALESCE(SUM(l.credit),0.0),"
                " COALESCE(sum(debit-credit), 0.0) "
                "FROM account_move_line AS l,  "
                "account_move AS m "
                "WHERE l.partner_id = %s "
                "AND m.id = l.move_id "
                "AND m.state IN %s "
                "AND account_id IN %s"
                " " + RECONCILE_TAG + " "
                "AND " + query + "  "
            ),
            (partner.id, tuple(move_state), tuple(self.account_ids)))

        res = self.cr.fetchall()

        return res

report_sxw.report_sxw(
    'report.account_partner_ledger.account_partner_ledger',
    'res.partner',
    'addons/account_partner_ledger/report/account_partner_ledger.rml',
    parser=account_partner_ledger,
    header=False
)
