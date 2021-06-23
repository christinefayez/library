from odoo import models, api, fields
from odoo.exceptions import ValidationError


class LibraryBookCateg(models.Model):
    _name = 'library.book.category'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char('Category')

    # def _print(self):
    #     print('hello')
    # co_field = fields.Date(string="",store=True, required=False, compute="_print")
    parent_id = fields.Many2one(
        'library.book.category',
        string='Parent Category',
        ondelete='restrict',
        index=True)
    child_ids = fields.One2many('library.book.category', 'parent_id', string='Child Categories')
    parent_path = fields.Char(index=True)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')

    def _check_recursion(self):
        _sql_constraints = [
            ('uniq_number', 'UNIQUE(name)', 'This number is already taken'), ]
