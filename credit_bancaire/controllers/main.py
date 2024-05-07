# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from operator import itemgetter

from odoo import http, _
from odoo.http import request
from odoo.osv.expression import AND, OR
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager

class BudgetPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        print(values)
        if 'budget_count' in counters:
            domain = self._get_portal_default_domain()
            values['budget_count'] = request.env['budget.request'].search_count(domain)
        print(values)
        return values

    def _get_portal_default_domain(self):
        my_user = request.env.user
        return [
            ('user_id', '=', my_user.id),
        ]

    def _get_appointment_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('all', 'name'):
            search_domain = OR([search_domain, [('name', 'ilike', search)]])
        if search_in in ('all', 'responsible'):
            search_domain = OR([search_domain, [('user_id', 'ilike', search)]])
        if search_in in ('all', 'description'):
            search_domain = OR([search_domain, [('description', 'ilike', search)]])
        return search_domain

    def _appointment_get_groupby_mapping(self):
        return {
            'responsible': 'user_id',
        }

    @http.route(['/my/budgets',
                 '/my/budgets/page/<int:page>',
                ], type='http', auth='user', website=True)
    def portal_my_appointments(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kwargs):
        values = self._prepare_portal_layout_values()
        # Sudo to access the appointment name and responsible for the groupby
        Budget = request.env['budget.request'].sudo()
        print('in controller')
        domain = self._get_portal_default_domain()

        searchbar_sortings = {
            'date_start': {'label': _('Date Debut'), 'order': 'start_date'},
            'date_end': {'label': _('Date Fin'), 'order': 'end_date'},
            'name': {'label': _('Name'), 'order': 'name'},
            'amount': {'label': _('Montant'), 'order': 'amount'},
        }

        searchbar_inputs = {
            'all': {'label': _('Search in All'), 'input': 'all'},
            'name': {'label': _('Search in Name'), 'input': 'name'},
            'responsible': {'label': _('Search in Responsible'), 'input': 'responsible'},
        }

        searchbar_groupby = {
            'none': {'label': _('None'), 'input': 'none'},
            'responsible': {'label': _('Responsible'), 'input': 'responsible'},
        }

        searchbar_filters = {
            'all': {'label': _("All"), 'domain': []},
        }

        if not sortby:
            sortby = 'date_start'
        sort_order = searchbar_sortings[sortby]['order']
        groupby_mapping = self._appointment_get_groupby_mapping()
        groupby_field = groupby_mapping.get(groupby, None)
        if groupby_field is not None and groupby_field not in Budget._fields:
            raise ValueError(_("The field '%s' does not exist in the targeted model", groupby_field))
        order = '%s, %s' % (groupby_field, sort_order) if groupby_field else sort_order

        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain = AND([domain, self._get_appointment_search_domain(search_in, search)])

        budget_count = Budget.search_count(domain)
        pager = portal_pager(
            url="/my/budgets",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby},
            total=budget_count,
            page=page,
            step=self._items_per_page
        )
        budgets = Budget.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        grouped_budget = False
        # If not False, this will contain a list of tuples (record of groupby, recordset of events):
        # [(res.users(2), calendar.event(1, 2)), (...), ...]
        if groupby_field:
            grouped_budget = [(g, Budget.concat(*events)) for g, events in groupbyelem(budgets, itemgetter(groupby_field))]

        values.update({
            'budgets': budgets,
            'grouped_budget': grouped_budget,
            'page_name': 'budget',
            'pager': pager,
            'default_url': '/my/budgets',
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': searchbar_filters,
        })
        return request.render("credit_bancaire.portal_my_budgets", values)

    @http.route('/my/budgets/new', type='http', auth="public", website=True, csrf=True)
    def demande_form(self, **kwargs):
        return request.render("credit_bancaire.portal_my_budgets_new", {})

    @http.route(['/create/budget'], type='http', auth="public", website=True)
    def create_demande(self, **kwargs):
        print(kwargs)
        kwargs['user_id'] = request.env.user.id
        request.env['budget.request'].create(kwargs)
        return self.portal_my_appointments()
