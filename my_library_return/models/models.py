from odoo import models, fields, api
from datetime import timedelta


class LibraryBookInherit(models.Model):
    _inherit = 'library.book'

    date_return = fields.Date(string="Date To Return")

    def make_borrowed(self):
        day_to_borrow = self.category_id.max_borrow_days or 10
        self.date_return = fields.date.today() + timedelta(days=day_to_borrow)
        return super(LibraryBookInherit, self).make_borrowed()


class CategoryObject(models.Model):
    _inherit = 'library.book.category'

    max_borrow_days = fields.Integer(string="Maximum Borrow Days", default=10)
