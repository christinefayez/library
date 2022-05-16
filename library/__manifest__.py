{
    'name': "My library",
    'summary': "Manage books easily",
    'description': """
Manage Library
==============
Description related to library.
""",
    'author': "christine fayez",
    'website': "https://www.linkedin.com/in/christine-fayez-018593172",
    'version': '15.0.1',
    'category': 'Uncategorized',
    'depends': ['base'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/cron_job.xml',
        'data/library_book_data.xml',
        'views/library_book.xml',
        'views/views.xml',

    ],

    'demo': ['demo/demo.xml'],
}
