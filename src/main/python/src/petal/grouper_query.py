import logging

import requests

logger = logging.getLogger( __name__ )

class GrouperQuery( object ):

    def __init__( self, grouper_host, grouper_base_path, grouper_user, grouper_passwd, grouper_stem, grouper_group ):
        logger.debug( 'entered' )

        #
        # set properties

        self.grouper_host = grouper_host
        self.grouper_base_path = grouper_base_path
        self.grouper_user = grouper_user
        self.grouper_passwd = grouper_passwd
        self.grouper_stem = grouper_stem
        self.grouper_group = grouper_group

        self.grouper_group_members_url = 'https://%s/%s/%s:%s/members' % ( grouper_host, grouper_base_path, grouper_stem, grouper_group )

        #
        # execute grouper query and populate members property

        logger.debug( 'executing grouper query and compiling members' )

        try:
            rsp = requests.get( self.grouper_group_members_url, auth = ( grouper_user, grouper_passwd ) )
            rsp.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logger.error( ':x: http error: `%s`', errh )
            logger.error( ':x: response: `%s`', errh.response.text )
            raise
        except requests.exceptions.RequestException as e:
            logger.error( ':x: error: `%s`', e )
            raise

        if 'wsSubjects' in rsp.json()['WsGetMembersLiteResult']:
            self._members = { s['id'] for s in rsp.json()['WsGetMembersLiteResult']['wsSubjects'] }
        else:
            self._members = []

        logger.debug( 'returning' )
        return

    @property
    def members( self ):
        logger.debug( 'entered' )

        logger.debug( 'returning' )
        return set( self._members )
