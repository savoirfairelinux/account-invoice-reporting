from openerp.report import report_sxw
from account.report.account_print_overdue import Overdue

class OverdueReport(Overdue):
    def __init__(self, cr, uid, name, context):
        base_class = super(OverdueReport, self)
        base_class.__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'getLines': self._lines_get,
        })
        self.lines = None

    def _lines_get(self, partner):
        if self.lines:
            return self.lines

        base_class = super(OverdueReport, self)
        moveLines = base_class._lines_get(partner)

        balance = 0

        lines = []
        
        for line in moveLines:
            balance += line['debit'] - line['credit']

            current = {
                "date": line['date'],
                "account_id": line['account_id'],
                "credit": line['credit'],
                "debit": line['debit'],
                "ref": line['ref'],
                "date_maturity": line['date_maturity'],
                "balance": balance,
            }

            lines.append(current)

        self.lines = lines

        return lines


report_sxw.report_sxw(
    'report.account.overdue2',
    'res.partner',
    'addons/due_payments/report/account_print_overdue.rml',
    parser=OverdueReport
)
