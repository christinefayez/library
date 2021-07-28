{
    'name': "My library",
    'summary': "Manage books easily",
    'description': """
Manage Library
==============
Description related to library.
""",
    'author': "christine fayez",
    'website': "http://www.example.com",
    'category': 'Uncategorized',
    'version': '13.0.1',
    'depends': ['base'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/cron_job.xml',
        'views/library_book.xml',
        'views/views.xml',

    ],

    'demo': ['demo.xml'],
}
