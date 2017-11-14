__version__ = '1.2.1'

from .ldap_query import LDAPQuery
from .grouper_query import GrouperQuery
from .delta import Delta

#
# Best practice library logging setup.

import logging
logger = logging.getLogger( __name__ )
logger.addHandler( logging.NullHandler() )