{
    'name': "Daily_Sales_Report",
    'summary': "Daily sales reports with multiple filtering options",

    'description': """
 This module is designed for businesses that need to generate daily sales reports with multiple filtering options. It provides a detailed overview of sales performance, payment status, and delivery progress, all available in a downloadable Excel format.
    """,
    'author': "Amzsys",
    'website': "https://www.amzsys.com",
    'category': 'Uncategorized',
    'version': '0.1',
     'depends': ['base', 'sale', 'account','sale_management'],
   'data': [
         'security/ir.model.access.csv',
        'Wizard/wizard.xml',
    ],

}
