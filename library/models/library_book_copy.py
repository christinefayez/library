from odoo import models, fields, api


class LibraryBookCopy(models.Model):
    _name = 'library.book.copy'


class ArchiveAbs(models.AbstractModel):
    _name = 'base.archive'

    active = fields.Boolean(default=True)

    def do_archive(self):
        for rec in self:
            rec.active = not rec.active

            print(rec.active)
