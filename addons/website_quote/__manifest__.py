# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Online Proposals',
    'category': 'Sales',
    'summary': 'Build quotation templates',
    'website': 'https://www.odoo.com/page/quote-builder',
    'version': '1.0',
    'description': "This module allows to create polished, professional proposals using templates. Templates come with default products, options, terms & conditions and confirmation methods (sign, pay).",
    'depends': ['website', 'sale_management', 'mail', 'sale_payment', 'website_mail'],
    'data': [
        'data/website_quote_data.xml',
        'report/sale_order_reports.xml',
        'report/sale_order_templates.xml',
        'report/website_quote_templates.xml',
        'views/sale_order_views.xml',
        'views/sale_quote_views.xml',
        'views/website_quote_templates.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'data/website_quote_demo.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
