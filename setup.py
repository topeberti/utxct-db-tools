from setuptools import setup, find_packages

setup(
    name='dbtools',  # Change this to a valid name, e.g., 'myqueries'
    version='0.1.9',
    packages=find_packages(),
    install_requires=["psycopg2-binary", "python-dotenv"],
    author='Alberto Vicente del Egido',
    description='Database utilities for IMDEA database',
    url='https://github.com/topeberti/utxct-db-tools', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
