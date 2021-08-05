__version__ = '1.6.7'

import logging

from .delta import Delta
from .grouper_query import GrouperQuery
from .ldap_query import LDAPQuery

#
# Best practice library logging setup.

logger = logging.getLogger( __name__ )
logger.addHandler( logging.NullHandler() )
