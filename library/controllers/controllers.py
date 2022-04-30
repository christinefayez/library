# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception
from werkzeug.wrappers import Response


class Library(http.Controller):
    @http.route('/library', type='http', auth='none', website=True, methods=['GET'])
    def index(self):
        response = {'success': True}
        library = request.env['library.book'].sudo().search([])

        if library:

            libary_books = []
            for lib in library:
                data = {
                    'name': lib.name,
                    'id': lib.id
                }
                libary_books.append(data)
            response['library_books'] = libary_books
        else:
            response = {'success': False}
        print(response)
        return response
