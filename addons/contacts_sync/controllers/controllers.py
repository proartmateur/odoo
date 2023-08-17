# -*- coding: utf-8 -*-
# from odoo import http


# class ContactsSync(http.Controller):
#     @http.route('/contacts_sync/contacts_sync', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contacts_sync/contacts_sync/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contacts_sync.listing', {
#             'root': '/contacts_sync/contacts_sync',
#             'objects': http.request.env['contacts_sync.contacts_sync'].search([]),
#         })

#     @http.route('/contacts_sync/contacts_sync/objects/<model("contacts_sync.contacts_sync"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contacts_sync.object', {
#             'object': obj
#         })
