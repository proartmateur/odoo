# -*- coding: utf-8 -*-
import json

from odoo import http
import requests



class APrueba(http.Controller):
    @http.route('/a_prueba/a_prueba', auth='public')
    def index(self, **kw):
        rick_api_url = "https://rickandmortyapi.com/api/character"
        chars = requests.get(rick_api_url)
        print("chars.content:")

        return f"Hello, world: {str(chars.content)}"

    @http.route('/a_prueba/a_prueba/objects', auth='public')
    def list(self, **kw):
        return http.request.render('a_prueba.listing', {
            'root': '/a_prueba/a_prueba',
            'objects': http.request.env['a_prueba.a_prueba'].search([]),
        })

    @http.route('/a_prueba/a_prueba/objects/<model("a_prueba.a_prueba"):obj>', auth='public')
    def object(self, obj, **kw):
        return http.request.render('a_prueba.object', {
            'object': obj
        })
