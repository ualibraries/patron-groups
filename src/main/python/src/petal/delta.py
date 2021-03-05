import datetime
import json
import logging
import time

import requests

logger = logging.getLogger( __name__ )

class Delta( object ):

    def __init__( self, ldap_query_instance, grouper_query_instance, batch_size, batch_timeout, batch_delay, sync_max ):
        logger.debug( 'entered' )

        self.ldap_query_instance = ldap_query_instance
        self.grouper_query_instance = grouper_query_instance
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.batch_delay = batch_delay
        self.sync_max = sync_max

        logger.debug( 'returning' )
        return

    @property
    def common( self ):
        logger.debug( 'entered' )

        common = self.ldap_query_instance.members & self.grouper_query_instance.members

        logger.debug( 'returning' )
        return common

    @property
    def adds( self ):
        logger.debug( 'entered' )

        adds = self.ldap_query_instance.members - self.grouper_query_instance.members

        logger.debug( 'returning' )
        return adds

    @property
    def drops( self ):
        logger.debug( 'entered' )

        drops = self.grouper_query_instance.members - self.ldap_query_instance.members

        logger.debug( 'returning' )
        return drops

    def synchronize( self ):
        logger.debug( 'entered' )

        total_delta = len( list( self.adds ) ) + len( list( self.drops ) )
        if total_delta > self.sync_max:
            logger.warn( 'total delta (%d) exceeds maximum sync limit (%d), will not synchronize' % ( total_delta, self.sync_max ) )
            logger.debug( 'returning' )
            return

        logger.info( 'synchronizing ldap query results to %s' % ( self.grouper_query_instance.grouper_group ) )
        logger.debug( 'batch size = %d, batch timeout = %d seconds, batch delay = %d seconds' % ( self.batch_size, self.batch_timeout, self.batch_delay ) )

        logger.debug( 'processing drops:' )
        n_batches = 0
        list_of_drops = list( self.drops )
        for batch in [ list_of_drops[i:i + self.batch_size] for i in range( 0, len( list_of_drops ), self.batch_size ) ]:
            n_batches += 1

            start_t = datetime.datetime.now()

            try:
                rsp = requests.post( self.grouper_query_instance.grouper_group_members_url,
                                     auth = ( self.grouper_query_instance.grouper_user, self.grouper_query_instance.grouper_passwd ),
                                     data = json.dumps( {
                                                            'WsRestDeleteMemberRequest': {
                                                                'replaceAllExisting': 'F',
                                                                'subjectLookups': [ { 'subjectId': entry } for entry in batch ]
                                                            }
                                                        } ),
                                     headers = { 'Content-type': 'text/x-json' },
                                     timeout = self.batch_timeout )
                rsp.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                logger.warn( ':x: http error: `%s`', errh )
            except requests.exceptions.RequestException as e:
                logger.error( ':x: error: `%s`', e )
                raise

            end_t = datetime.datetime.now()
            batch_t = ( end_t - start_t ).total_seconds()

            rsp_j = rsp.json()
            if rsp_j['WsDeleteMemberResults']['resultMetadata']['resultCode'] not in ( 'SUCCESS' ):
                logger.warn( 'problem running batch delete, result code = %s',
                             rsp_j['WsDeleteMemberResults']['resultMetadata']['resultCode'] )
            else:
                logger.info( 'dropped batch %d, %d entries, %d seconds' % ( n_batches, len( batch ), batch_t ) )

            if self.batch_delay > 0:
                logger.info( 'pausing for %d seconds' % ( self.batch_delay ) )
                time.sleep( self.batch_delay )

        logger.debug( 'processing adds:' )
        n_batches = 0
        list_of_adds = list( self.adds )
        for batch in [ list_of_adds[i:i + self.batch_size] for i in range( 0, len( list_of_adds ), self.batch_size ) ]:
            n_batches += 1

            start_t = datetime.datetime.now()

            try:
                rsp = requests.put( self.grouper_query_instance.grouper_group_members_url,
                                    auth = ( self.grouper_query_instance.grouper_user, self.grouper_query_instance.grouper_passwd ),
                                    data = json.dumps( {
                                                        'WsRestAddMemberRequest': {
                                                            'replaceAllExisting': 'F',
                                                            'subjectLookups': [ { 'subjectId': entry } for entry in batch ]
                                                            }
                                                    } ),
                                    headers = { 'Content-type': 'text/x-json' },
                                    timeout = self.batch_timeout )
                rsp.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                logger.warn( ':x: http error: `%s`', errh )
            except requests.exceptions.RequestException as e:
                logger.error( ':x: error: `%s`', e )
                raise

            end_t = datetime.datetime.now()
            batch_t = ( end_t - start_t ).total_seconds()

            rsp_j = rsp.json()
            if rsp_j['WsAddMemberResults']['resultMetadata']['resultCode'] not in ( 'SUCCESS' ):
                logger.warn( 'problem running batch add, result code = %s',
                             rsp_j['WsAddMemberResults']['resultMetadata']['resultCode'] )
                logger.warn( 'result message: %s',
                             rsp_j['WsAddMemberResults']['resultMetadata']['resultMessage'] )

                logger.warn( '  failures:')
                for result in rsp_j['WsAddMemberResults']['results']:
                    if result['resultMetadata']['resultCode'] not in ( 'SUCCESS' ):
                        logger.warn( '    %s', result['wsSubject']['id'] )

            else:
                logger.info( 'added batch %d, %d entries, %d seconds' % ( n_batches, len( batch ), batch_t ) )

            if self.batch_delay > 0:
                logger.info( 'pausing for %d seconds' % ( self.batch_delay ) )
                time.sleep( self.batch_delay )

        logger.debug( 'returning' )
        return
