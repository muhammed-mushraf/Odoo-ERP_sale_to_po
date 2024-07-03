{
    'name': 'Dig sales',
    'depends': ['sale','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_inherit.xml',
        'views/sequence.xml',
        'views/vendor.xml',
    ],
    'instalable': True,
    'sequence': 1,
    'application': True,
    'assets': {
                'web.assets_backend': ['dgz_sales/static/src/css/lock.css']
            }
}
