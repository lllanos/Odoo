# -*- coding: utf-8 -*-

{
    'name': 'Website Payment',
    'category': 'Technical Settings',
    'summary': 'Payment integration with website',
    'version': '1.0',
    'description': """
This is a bridge module which integrates payment acquirers with Website app.
    """,
    'depends': [
        'website',
        'payment',
        'portal',
    ],
    'data': [
        'views/website_payment_view.xml',
    ],
    'auto_install': False,
}
