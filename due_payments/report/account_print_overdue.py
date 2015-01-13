from openerp.report import report_sxw
from account.report.account_print_overdue import Overdue

report_sxw.report_sxw(
    'report.account.overdue2',
    'res.partner',
    'addons/due_payments/report/account_print_overdue.rml',
    parser=Overdue
)
