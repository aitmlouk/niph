{
    'name': 'Modifications NIPH ',
    'version': '13',
    'author': 'ait mlouk brahim',
    'website': 'http://www.learn.odoo.com',
    'support': 'aitmlouk98@gmail.com',
    'licence': 'AGPL-3',
    'complexity': 'easy',
    'sequence': 1,
    'category': 'category',
    'description': """
       Modifications NIPH 
           -module1
           -module2
           -module3


     """,
    'depends': ['base', 'mail','product','account', 'sale_stock', 'purchase','sale'],
    'summary': 'odoo13 , python ',
    'data': [

        'security/ir.model.access.csv',
        'views/modif_niph_inherit.xml',
        'views/modif_niph.xml',
        'wizard/wiz_view.xml',
        'menu.xml',
    ],
    'demo': [

    ],
    'css': [

    ],
    'price': 100.00,
    'currency': 'EUR',
    'instalable': True,
    'application': True,

}