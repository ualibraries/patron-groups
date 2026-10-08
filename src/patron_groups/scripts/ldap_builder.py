"""Interactive helper for building custom LDAP queries and cross-referencing them against petl groups.

Credentials come from the project's .env file (PGRPS_LDAP_PASSWD); host, base DN, bind user and the
per-group queries come from config/petl.ini.

Usage:  python ldap_builder.py [--env PATH] [--config PATH]
"""

import argparse
import configparser
import os
import re
import sys
from pathlib import Path

import ldap3
from ldap3.utils.conv import escape_filter_chars

HERE = Path( __file__ ).resolve().parent
DEFAULT_CONFIG = HERE.parent / 'config' / 'petl.ini'
DEFAULT_ENV = HERE.parents[2] / '.env'

OPERATORS = {
    '=':  'equals',
    '~=': 'approximately equals',
    '>=': 'greater than or equal',
    '<=': 'less than or equal',
    '*':  'present (any value)',
}

#
# config / environment

def load_env( path ):
    """Minimal .env parser (KEY=VALUE, # comments, optional quotes); does not override real env vars."""
    if not path.is_file():
        sys.exit( f'env file not found: {path}' )
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith( '#' ) or '=' not in line:
            continue
        key, _, value = line.partition( '=' )
        value = value.strip().strip( '"\'' )
        os.environ.setdefault( key.strip().removeprefix( 'export ' ), value )

def load_config( path ):
    cp = configparser.ConfigParser( interpolation = None )
    cp.read( path )
    glob = dict( cp['global'] )
    glob['ldap_passwd'] = os.environ.get( 'PGRPS_LDAP_PASSWD', '' )
    groups = {}
    for name in cp.sections():
        if name == 'global' or not cp.has_option( name, 'ldap_query' ):
            continue
        # collapse the indented multi-line filter into a single compact string
        groups[name] = re.sub( r'\s+', '', cp.get( name, 'ldap_query' ) )
    return glob, groups

#
# ldap

class Directory( object ):

    def __init__( self, cfg ):
        if not cfg['ldap_passwd']:
            sys.exit( 'PGRPS_LDAP_PASSWD is not set in the env file' )
        self.search_dn = 'ou=people,' + cfg['ldap_base_dn']
        bind_dn = f"uid={cfg['ldap_user']},ou=app users,{cfg['ldap_base_dn']}"
        self.conn = ldap3.Connection( 'ldaps://' + cfg['ldap_host'], bind_dn, cfg['ldap_passwd'], auto_bind = True,
                                     read_only = True )  # never allow writes to the directory

    def search( self, query, attributes ):
        """Return a list of attribute dicts for every entry matching query (paged)."""
        results = self.conn.extend.standard.paged_search(
            self.search_dn, query, attributes = attributes, paged_size = 500, generator = True )
        return [ r['attributes'] for r in results if r.get( 'type' ) == 'searchResEntry' ]

    def uaids( self, query ):
        return { str( e['uaid'] ) for e in self.search( query, ['uaid'] ) if e.get( 'uaid' ) }

#
# filter building

def clause( attr, op, values, wildcards ):
    """Build (attr op value) for one value, or an OR of them for several."""
    def one( v ):
        if op == '*':
            return f'({attr}=*)'
        esc = escape_filter_chars( v )
        if wildcards:
            esc = esc.replace( '\\2a', '*' )
        return f'({attr}{op}{esc})'
    parts = [ one( v ) for v in values ] if op != '*' else [ one( '' ) ]
    return parts[0] if len( parts ) == 1 else '(|' + ''.join( parts ) + ')'

def combine( joiner, parts ):
    parts = [ p for p in parts if p ]
    if not parts:
        return ''
    return parts[0] if len( parts ) == 1 else f'({joiner}' + ''.join( parts ) + ')'

def pretty( flt, indent = 4 ):
    """Indent an LDAP filter by parenthesis depth for display."""
    out, depth, i = [], 0, 0
    while i < len( flt ):
        if flt[i] == '(' and i + 1 < len( flt ) and flt[i + 1] in '&|!':
            out.append( ' ' * indent * depth + flt[i:i + 2] )
            depth += 1
            i += 2
        elif flt[i] == '(':
            j = flt.index( ')', i )
            out.append( ' ' * indent * depth + flt[i:j + 1] )
            i = j + 1
        elif flt[i] == ')':
            depth -= 1
            i += 1
        else:
            i += 1
    return '\n'.join( out )

#
# prompts

def ask( prompt, default = None ):
    suffix = f' [{default}]' if default else ''
    try:
        answer = input( f'{prompt}{suffix}: ' ).strip()
    except EOFError:
        sys.exit( 0 )
    return answer or ( default or '' )

def pick_groups( groups, prompt ):
    names = list( groups )
    for i, n in enumerate( names, 1 ):
        print( f'  {i:2}. {n}' )
    raw = ask( f'{prompt} (numbers/names, comma separated, blank for none)' )
    chosen = []
    for tok in filter( None, ( t.strip() for t in raw.split( ',' ) ) ):
        if tok.isdigit() and 1 <= int( tok ) <= len( names ):
            chosen.append( names[int( tok ) - 1] )
        elif tok in groups:
            chosen.append( tok )
        else:
            print( f'  ignoring unknown group: {tok}' )
    return chosen

def build_conditions():
    """Prompt for attribute conditions until the user is done; returns (list of clauses, joiner)."""
    print( '\nOperators: ' + ', '.join( f'{k} ({v})' for k, v in OPERATORS.items() ) )
    print( 'Multiple values for one attribute are OR-ed. Use * inside values as a wildcard, e.g. studentcpp=*:*:UGRD:*:*:*:*:AC:*:*' )
    clauses = []
    while True:
        attr = ask( '\nAttribute (blank to finish)' )
        if not attr:
            break
        op = ask( 'Operator', '=' )
        if op not in OPERATORS:
            print( '  unknown operator' )
            continue
        values = []
        if op != '*':
            values = [ v.strip() for v in ask( 'Value(s), comma separated' ).split( ',' ) if v.strip() ]
            if not values:
                print( '  no values given' )
                continue
        c = clause( attr, op, values, wildcards = True )
        if ask( 'Negate this condition? (y/n)', 'n' ).lower().startswith( 'y' ):
            c = f'(!{c})'
        clauses.append( c )
        print( f'  added: {c}' )
    joiner = '&'
    if len( clauses ) > 1:
        joiner = '&' if ask( 'Join conditions with AND or OR?', 'AND' ).upper() != 'OR' else '|'
    return clauses, joiner

#
# actions

def cross_reference( d, groups, query, cross_attrs ):
    """Count how many custom-query matches fall into each selected group, and optionally break down attributes."""
    attrs = [ 'uaid' ] + cross_attrs
    print( '\nRunning custom query...' )
    entries = d.search( query, attrs )
    mine = { str( e['uaid'] ): e for e in entries if e.get( 'uaid' ) }
    print( f'Custom query matched {len( mine )} people.' )
    if not mine:
        return

    chosen = pick_groups( groups, '\nGroups to cross-reference against' )
    memberships = {}
    for g in chosen:
        print( f'  loading {g}...' )
        memberships[g] = d.uaids( groups[g] )

    if chosen:
        print( f'\n{"group":38} {"group size":>10} {"overlap":>9} {"% of query":>11} {"only in query":>14} {"only in group":>14}' )
        for g, members in memberships.items():
            both = mine.keys() & members
            print( f'{g:38} {len( members ):>10} {len( both ):>9} {100 * len( both ) / len( mine ):>10.1f}% '
                   f'{len( mine.keys() - members ):>14} {len( members - mine.keys() ):>14}' )
        in_none = mine.keys() - set().union( *memberships.values() )
        print( f'\nMatched by the custom query but in none of the selected groups: {len( in_none )}' )

    if cross_attrs:
        print( '\nAttribute value breakdown of custom-query matches:' )
        for a in cross_attrs:
            counts = {}
            for e in mine.values():
                v = e.get( a )
                for item in ( v if isinstance( v, list ) else [v] ):
                    counts[str( item )] = counts.get( str( item ), 0 ) + 1
            print( f'  {a}:' )
            for val, n in sorted( counts.items(), key = lambda kv: -kv[1] )[:15]:
                print( f'    {n:>7}  {val}' )

    return mine

def main():
    ap = argparse.ArgumentParser( description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter )
    ap.add_argument( '--env', type = Path, default = DEFAULT_ENV )
    ap.add_argument( '--config', type = Path, default = DEFAULT_CONFIG )
    args = ap.parse_args()

    load_env( args.env )
    cfg, groups = load_config( args.config )
    d = None  # connect lazily so building/printing filters works offline

    query = ''
    while True:
        print( '\n=== LDAP query builder ===' )
        print( f'Current query: {query or "(none)"}' )
        print( '  1. List configured groups' )
        print( '  2. Show a group\'s query' )
        print( '  3. Build a query from attributes' )
        print( '  4. Start from / combine with configured groups' )
        print( '  5. Show current query (pretty)' )
        print( '  6. Run query and cross-reference member groups' )
        print( '  7. Enter a raw filter' )
        print( '  q. Quit' )
        choice = ask( 'Choice' ).lower()

        if choice == '1':
            for n in groups:
                print( f'  {n}' )
        elif choice == '2':
            for g in pick_groups( groups, 'Group' ):
                print( f'\n[{g}]\n{pretty( groups[g] )}' )
        elif choice == '3':
            clauses, joiner = build_conditions()
            built = combine( joiner, clauses )
            if not built:
                continue
            if query:
                mode = ask( 'Combine with current query using AND, OR, or REPLACE?', 'AND' ).upper()
                if mode in ( 'AND', 'OR' ):
                    built = combine( '|' if mode == 'OR' else '&', [ query, built ] )
            query = built
        elif choice == '4':
            chosen = pick_groups( groups, 'Groups' )
            if chosen:
                joiner = '|' if ask( 'Join groups with AND or OR?', 'OR' ).upper() == 'OR' else '&'
                combined = combine( joiner, [ groups[g] for g in chosen ] )
                if query and ask( 'Combine with current query? (y/n)', 'n' ).lower().startswith( 'y' ):
                    j2 = '|' if ask( 'Join with AND or OR?', 'AND' ).upper() == 'OR' else '&'
                    combined = combine( j2, [ query, combined ] )
                query = combined
        elif choice == '5':
            print( pretty( query ) if query else '(no query)' )
        elif choice == '6':
            if not query:
                print( 'Build a query first.' )
                continue
            extra = [ a.strip() for a in ask( 'Extra attributes to summarize (comma separated, blank for none)' ).split( ',' ) if a.strip() ]
            try:
                d = d or Directory( cfg )
                mine = cross_reference( d, groups, query, extra )
            except ldap3.core.exceptions.LDAPException as e:
                print( f'LDAP error: {e}' )
                continue
            if mine:
                path = ask( 'Save matching uaids to file (blank to skip)' )
                if path:
                    out = Path( path ).expanduser()
                    if out.is_dir():
                        print( f'  {out} is a directory, not saving' )
                    elif out.exists() and not ask( f'{out} exists, overwrite? (y/n)', 'n' ).lower().startswith( 'y' ):
                        print( '  not saved' )
                    else:
                        out.write_text( '\n'.join( sorted( mine ) ) + '\n' )
                        print( f'  wrote {len( mine )} uaids to {out}' )
        elif choice == '7':
            query = ask( 'Filter' ) or query
        elif choice in ( 'q', 'quit', 'exit' ):
            break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
