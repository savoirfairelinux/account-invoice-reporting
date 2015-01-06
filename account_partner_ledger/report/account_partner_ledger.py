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


class account_partner_ledger(third_party_ledger):
    def __init__(self, cr, uid, name, context=None):
        base_class = super(account_partner_ledger, self)
        base_class.__init__(cr, uid, name, context=context)
        import pdb; pdb.set_trace()

report_sxw.report_sxw(
    'report.account_partner_ledger.account_partner_ledger',
    'res.partner',
    'addons/account_partner_ledger/report/account_partner_ledger.rml',
    parser=account_partner_ledger,
    header='external',
)
