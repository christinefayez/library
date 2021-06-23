from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

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
         ('lost', 'Lost')],
        'State', default="draft")

    description = fields.Html('Description', sanitize=True, strip_style=False)
    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependent=False)
    active = fields.Boolean('Active', default=True)
    cost_price = fields.Float('Book Cost', digits='Book Price')
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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')
    authored_book_ids = fields.Many2many('library.book', string='Authored Books')
