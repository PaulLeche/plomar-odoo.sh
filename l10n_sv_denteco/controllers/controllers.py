# -*- coding: utf-8 -*-
# from odoo import http


# class L10nSvDenteco(http.Controller):
#     @http.route('/l10n_sv_denteco/l10n_sv_denteco', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_sv_denteco/l10n_sv_denteco/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_sv_denteco.listing', {
#             'root': '/l10n_sv_denteco/l10n_sv_denteco',
#             'objects': http.request.env['l10n_sv_denteco.l10n_sv_denteco'].search([]),
#         })

#     @http.route('/l10n_sv_denteco/l10n_sv_denteco/objects/<model("l10n_sv_denteco.l10n_sv_denteco"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_sv_denteco.object', {
#             'object': obj
#         })

