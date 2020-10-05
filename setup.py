from setuptools import find_packages, setup

setup(
    name='flaskIdea',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'jaydebeapi',
        'pandas',
        'xlwt',
        'pyodbc',
        'flask-bootstrap',
        'flask-wtf',
        'flask-sqlalchemy',
        'flask-login',
        'wtforms',
        'werkzeug',
        'sqlalchemy',
        'email_validator',
        'matplotlib',
    ],
)