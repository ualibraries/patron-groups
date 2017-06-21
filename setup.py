from setuptools import setup, find_packages
from src.petal import __version__

setup(

    name                 = 'Petal',
    version              = __version__,
    packages             = find_packages( 'src' ),
    package_dir          = { '': 'src' },
    entry_points = {
    },

    install_requires     = [ 'ldap3', 'requests' ],

    author               = 'Mike Simpson',
    author_email         = 'mgsimpson@email.arizona.edu',
    description          = 'Simple EDS-to-Grouper ETL scripting and supporting library.',
    license              = 'BSD 2-Clause',
    url                  = 'https://github.com/ualibraries/tess-petal',
    
    classifiers = [
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
    ],
)
