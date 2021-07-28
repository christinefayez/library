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
        print('jjjjjjjjjjjjjjjjjjj')

    def name_get(self):
        result = []
        for rec in self:
            rec_name = "%s (%s)" % (rec.name, rec.date_release)
            result.append((rec.id, rec_name))
        return result

    notes = fields.Text('Internal Notes')
    name = fields.Char('Title', required=True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many(
        'res.partner',
        string='Authors'
    )

    cover = fields.Binary('Book Cover')
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

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                print("hhhhhhhhhhhh")
                book.age_days = delta.days
            else:
                print("eeeeeeee")

                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()

        for book in self.filtered('date_release'):
            print('hcjhjhxuggg')
            d = today - timedelta(days=book.age_days)
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
        print(old_state, new_state)

    def change_state(self, new_state):
        for book in self:
            print('sssssssssssssss')
            if book.is_allowed_trainstion(book.state, new_state):
                print('jjjjjjjjjjjjjjjjj')
                book.state = new_state
                print(book.state, new_state)
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
        print(library_member_model)
        return True

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    def chang_date_update(self):
        self.ensure_one()
        self.update({

            'date_release': fields.Datetime.now()
        })

    def find_book(self):
        domain = [
            ('name', 'ilike', 'odoo12')
        ]
        book = self.search(domain)

        print(book)

    def books_with_multiple_author(self):

        books = self.filtered(lambda l: len(l.author_ids) > 1)
        print(books)

    def books_mapped_author(self):
        books = self.mapped('author_ids.name')
        count = 0
        for bo in books:
            count += 1
            print(count, bo)
        return books


class ResPartner(models.Model):
    _inherit = 'res.partner'

    published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')
    authored_book_ids = fields.Many2many('library.book', string='Authored Books')
    count_books = fields.Integer(string="Number Of Authored Books", compute="_compute_count_books")

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)
