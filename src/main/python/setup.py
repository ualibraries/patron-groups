from setuptools import setup, find_packages
from src.petal import __version__

setup(

    name                 = 'petal',
    version              = __version__,
    packages             = find_packages( 'src' ),
    package_dir          = { '': 'src' },
    scripts              = [ 
        'scripts/petl',
    ],
    data_files           = [
        ( '/etc/petal', [ 'config/incommon_rsa_ca_bundle.pem', 
                          'config/petl.ini' ] ),
    ],

    install_requires     = [ 'certifi', 'ldap3', 'requests', 'slack_log_handler' ],

    author               = 'Mike Simpson',
    author_email         = 'mgsimpson@email.arizona.edu',
    description          = 'Simple EDS-to-Grouper ETL scripting and supporting library.',
    license              = 'BSD 2-Clause',
    url                  = 'https://github.com/ualibraries/patron-groups',
    
    classifiers = [
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
    ],
)
