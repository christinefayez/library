from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    usage = fields.Selection(default=False)


class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['base.archive']
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

    def test_cron_library(self):
        pass

    def name_get(self):
        result = []
        for rec in self:
            authors = rec.author_ids.mapped('name')
            rec_name = "%s (%s)" % (rec.name, ','.join(authors))
            result.append((rec.id, rec_name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        print('login search')
        args = [] if args is None else args.copy()
        if not (name == ' ' and operator == 'ilike'):
            args += ['|', '|', ('name', operator, name),
                     ('isban', operator, name),
                     ('author_ids.name', operator, name)]
            print('args=====', args)
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    notes = fields.Text('Internal Notes')
    old_edition = fields.Many2one(comodel_name="library.book")
    name = fields.Char('Title', required=True)
    isban = fields.Char('ISBAN', required=True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many(
        'res.partner',
        string='Authors'
    )

    cover = fields.Binary('Book Cover')
    manager_remarkes = fields.Text(string="Manager Remarks", required=False, )
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date', default=fields.Date.today())
    date_updated = fields.Datetime('Last Updated', default=fields.Datetime.now())
    reader_rating = fields.Float(
        'Reader Average Rating',
        digits=(14, 4),
    )
    short_name = fields.Char('Short Title', translate=True, index=True)
    state = fields.Selection(
        [('draft', 'Not Available'),
         ('available', 'Available'),
         ('lost', 'Lost'), ('borrowed', 'Borrowed')],
        'State', default="draft")

    description = fields.Html('Description', sanitize=True, strip_style=False)
    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependent=False)
    active = fields.Boolean('Active', default=True)
    cost_price = fields.Float('Book Cost', digits='Book Price')
    ref_doc_id = fields.Reference(selection='_referencable_models')
    currency_id = fields.Many2one(
        'res.currency', string='Currency')

    retail_price = fields.Monetary(
        'Retail Price',
        # optional: currency_field='currency_id',
    )

    publisher_id = fields.Many2one('res.partner', string='Publisher', )
    publisher_city = fields.Char(readonly=True, related="publisher_id.city")
    category_id = fields.Many2one('library.book.category')
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        store=True,
        # optional
        compute_sudo=True  # optional
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',
         'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)',
         'No of pages must be positive')
    ]

    def get_average_cost(self):
        grouped_result = self.read_group([('cost_price', '!=', False)], ['category_id', 'average:avg(cost_price)'],
                                         ['category_id'],lazy=False)
        print(grouped_result)
        for p in grouped_result:
            print(p['average'])

        return grouped_result

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:

                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()

        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            print(d)
            print('dataaaaaaa',book.date_release)
        book.date_release = d

    @api.constrains('date_release')
    def _check_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError("date must be in the past")

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    @api.model
    def is_allowed_trainstion(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_trainstion(book.state, new_state):
                book.state = new_state
            else:
                msg = _('moving from %s to %s is not allowed') % (book.state, new_state)
                raise ValidationError(msg)
                continue

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_available(self):
        self.change_state('available')

    def make_lost(self):
        self.change_state('lost')

    def log_all_library_members(self):
        library_member_model = self.env['library.member'].search([])
        return True

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    def chang_date_update(self):
        self.ensure_one()
        self.write({

            'date_release': fields.Datetime.now()
        })

    def find_book(self):
        domain = [
            ('name', 'ilike', 'odoo12')
        ]
        book = self.search(domain)
        print(book)

        com = self.search([('active', '=', True)])
        com2 = self.search([('pages', '!=', 0)])
        print(com | com2, 'compination record set with no duplicate')

    def books_with_multiple_author(self):

        books = self.filtered(lambda l: len(l.author_ids) > 1)
        categ = self.filtered('category_id')
        print('books filter===========', books, categ)

    def get_books(self):
        books = self.search([])
        self.books_mapped_author(books)

    def books_mapped_author(self, books):
        bookss = books.mapped('author_ids.name')
        print(bookss, 'books======')
        count = 0
        for bo in bookss:
            count += 1
            print(count, bo)
        return bookss

    @api.model
    def create(self, vals):
        if not self.user_has_groups('library.group_librarian'):
            if 'manager_remarkes' in vals and vals['manager_remarkes']:
                raise UserError(_('u are not allowed to modify manager remarkes'))
        return super(LibraryBook, self).create(vals)

    def write(self, vals):
        if not self.user_has_groups('library.group_librarian'):
            if 'manager_remarkes' in vals and vals['manager_remarkes']:
                del vals['manager_remarkes']
        return super(LibraryBook, self).write(vals)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')
    authored_book_ids = fields.Many2many('library.book', string='Authored Books')
    count_books = fields.Integer(string="Number Of Authored Books", compute="_compute_count_books")

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)
