import logging

import ldap3

logger = logging.getLogger( __name__ )

class LDAPQuery( object ):

    def __init__( self, ldap_host, ldap_base_dn, ldap_user, ldap_passwd, ldap_query ):
        logger.debug( 'entered' )

        #
        # set properties

        self.ldap_host = ldap_host
        self.ldap_base_dn = ldap_base_dn
        self.ldap_user = ldap_user
        self.ldap_passwd = ldap_passwd
        self.ldap_query = ldap_query

        self.ldap_bind_host = 'ldaps://' + ldap_host
        self.ldap_bind_dn = 'uid=' + ldap_user + ',ou=app users,' + ldap_base_dn
        self.ldap_search_dn = 'ou=people,' + ldap_base_dn
        self.ldap_attribs = [ 'uaid' ]

        #
        # execute ldap query and populate members property

        logger.debug( 'executing ldap query and compiling members' )

        ldc = ldap3.Connection( self.ldap_bind_host, self.ldap_bind_dn, self.ldap_passwd, auto_bind = True )
        ldc.search( self.ldap_search_dn, self.ldap_query, attributes = self.ldap_attribs )
        self._members = { e.uaid.value for e in ldc.entries }

        logger.debug( 'returning' )
        return

    @property
    def members( self ):
        logger.debug( 'entered' )

        logger.debug( 'returning' )
        return set( self._members )
