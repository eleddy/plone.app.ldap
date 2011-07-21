import ldap
from zope import schema
import logging

class InvalidDnError(schema.ValidationError):
    __doc__ = u'Please enter a valid DN. A valid DN varies from business to business, ' \
                'but should look something like "OU=something,DC=something,..."'

def isValidDn(value):
    try:
        ldap.dn.str2dn(value,0)
    except ldap.DECODING_ERROR:
        # this is a much more specific configuration error
        # ldap.DECODING_ERROR can mean a few things
        raise InvalidDnError
        
    return True