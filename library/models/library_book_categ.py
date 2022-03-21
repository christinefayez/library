from odoo import models, api, fields
from odoo.exceptions import ValidationError


class LibraryBookCateg(models.Model):
    _name = 'library.book.category'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char('Category')
    description = fields.Text(string="", required=False, )
    parent_id = fields.Many2one(
        'library.book.category',
        string='Parent Category',
        ondelete='restrict',
        index=True)
    child_ids = fields.One2many('library.book.category', 'parent_id', string='Child Categories')
    parent_path = fields.Char(index=True)

    def create_category(self):
        categ1 = {
            'name': 'child categ1',
            'description': 'desc categ1'
        }
        categ2 = {
            'name': 'child categ2',
            'description': 'desc categ2'

        }
        parent_categ = {
            'name': 'tinaaaaaaaaaa',
            'description': 'kkkkkkkkkkkkkkkkkkk',
            'child_ids':
                [(0, 0, categ1), (0, 0, categ2)]
        }

        record = self.create([categ1, categ2])

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! Youu cannot create recursive categories.')


class LibraryMembers(models.Model):
    _name = 'library.member'
    _rec_name = 'member_id'

    member_number = fields.Char()
    member_id = fields.Many2one(comodel_name="res.partner", delegate=True, ondelete='cascade')
    date_start = fields.Date(string="", required=False, )
    date_end = fields.Date(string="", required=False, )
    date_of_birth = fields.Date(string="", required=False, )
