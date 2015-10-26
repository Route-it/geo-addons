# -*- coding: utf-8 -*-
from openerp import http

# class GeoCertifications(http.Controller):
#     @http.route('/geo_certifications/geo_certifications/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/geo_certifications/geo_certifications/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('geo_certifications.listing', {
#             'root': '/geo_certifications/geo_certifications',
#             'objects': http.request.env['geo_certifications.geo_certifications'].search([]),
#         })

#     @http.route('/geo_certifications/geo_certifications/objects/<model("geo_certifications.geo_certifications"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('geo_certifications.object', {
#             'object': obj
#         })