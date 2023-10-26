# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception
from werkzeug.wrappers import Response


class Library(http.Controller):
    @http.route('/library', type='json', auth='none', methods=['GET'])
    def index(self):
        library = request.env['library.book'].sudo().search([])
        libary_books = []

        if library:
            for lib in library:
                data = {
                    'name': lib.name,
                    'isban': lib.isban,
                    'id': lib.id
                }
                libary_books.append(data)
        date = {'state': 200, 'response': libary_books, 'message': 'Success'}
        return date

    @http.route('/create/book', type='json', auth='none', methods=['POST'])
    def create_book(self, **rec):

        if rec['name']:
            vals = {
                'name': rec['name'],
                'isban': rec['isban'],
            }
            book = request.env['library.book'].sudo().create(vals)

            date = {'success': True, 'ID': book.id, 'message': 'Success'}

            return date

    @http.route('/edit/book/<id>', type='json', auth='none', methods=['Put'])
    def edit_book(self,id,**vals):
        book=request.env['library.book'].sudo().browse(int(id))


        if 'name' in vals and vals['name'] and book:
            book.update(vals)

        date = {'success': True, 'response': [vals],'message': 'Success'}

        return date
