{
    'name': 'ARA HR AI Module Integrations Gemini - Smart Resume Scoring & Interview Questions',
    'version': '18.0.1.0.0',
    'category': '',
    'summary': 'Smart Resume Scoring & Interview Questions with Google Gemini AI for Odoo HR',
    'description': """
   
    """,
    'author': 'ARA SOFT',
    'depends': ['hr_recruitment'],
    "data": [
        "views/hr_applicant_views.xml",
        "views/res_company_views.xml",
    ],
    'external_dependencies': {
        'python': [
            'google-genai',
            'google-generativeai',  # library Gemini (package name di PyPI)
            'pymupdf',              # library fitz untuk baca PDF
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'price' :35,
    'currency' : 'USD',
    'images': ['static/description/banner_sale.gif'],
}
