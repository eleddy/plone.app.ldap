from Persistence import Persistent
from zope.interface import implements
from zope.app.container.ordered import OrderedContainer
from zope.app.container.interfaces import INameChooser
from plone.app.ldap.engine.interfaces import ILDAPServerStorage
from plone.app.ldap.engine.interfaces import ILDAPSchema
from plone.app.ldap.engine.interfaces import ILDAPConfiguration
from BTrees.OOBTree import OOBTree
from ldap import SCOPE_SUBTREE
from plone.app.ldap.engine.schema import LDAPProperty
from plone.app.ldap.ploneldap.util import lookupLDAPPlugin

# TODO: rename this to something more meaningful

class LDAPConfiguration(object):
    implements(ILDAPConfiguration)

    
    userid_attribute = "uid"
    login_attribute = "uid"
    user_object_classes = "pilotPerson"
    
    bind_password = ""
    user_base = ""
    user_scope = SCOPE_SUBTREE
    group_base = ""
    group_scope = SCOPE_SUBTREE
    password_encryption = ""
    default_user_roles = ""
    activated_interfaces = []
    activated_plugins = None
    cache = ''
    servers = {}
    
    _ldap_type = u"LDAP"
    _bind_dn = ""
    _rdn_attribute = "uid"
    _luf = None


    """
    For the setters, we go through manage because it clears
    the cache in the backend when it updates the attributes.
    Make sure the setter always updates the local config as 
    well so we don't have to check for luf each time.
    
    To display forms, having a pas plugin is not required. To
    edit them, however, it is. Currently this is assumed to be 
    done in controlpanel.py before these setters are hit. 
    """ 
    def getRdn_attribute(self):
        return self._rdn_attribute
        
    def setRdn_attribute(self, value):
        self._rdn_attribute = value
        # XXX; This made things pretty angry!
        #if self.luf:
        #    self.luf.manage_changeProperty('_rdnattr', value)
    
    
    def getLdap_type(self):
        return self._ldap_type
    
    def setLdap_type(self, value):
        # TODO: if we update the type, need to recreate 
        # the plugin
        self._ldap_type = value
        
    ldap_type = property(getLdap_type, setLdap_type)
    
    def getBind_dn(self):
        return self._bind_dn
    
    def setBind_dn(self, value):
        self._bind_dn = value
        if self.luf:
            self.luf.manage_changeProperty('_binduid', value)
        
    bind_dn = property(getBind_dn, setBind_dn)
    
    @property
    def luf(self):
        '''
        Get the LDAP user folder associated with this plugin 
        configuration. Don't get this on initialization since 
        the plugin may not exist yet
        '''
        plugin = lookupLDAPPlugin()
        if plugin:
            if not self._luf:
                self._luf = plugin._getLDAPUserFolder()
            return self._luf
            
        return None

    #@property
    #def plugin(self):
    #    '''
    #    Get the LDAPPlugin.
    #    '''
    ##    if not self._plugin:
    #        self._plugin = lookupLDAPPlugin()
    #    
    #    return self._plugin
    
    def __init__(self):
        self.schema = { "uid": LDAPProperty(description=u"User id", ldap_name="uid", ),
                        "mail": LDAPProperty(description=u"Email address", ldap_name="mail",
                                    plone_name="email"),
                        "cn": LDAPProperty(description=u"Canonical Name", ldap_name="cn",
                                    plone_name="fullname"),
                        "sn": LDAPProperty(description=u"Surname (unused)", ldap_name="sn",),
                      }
        
                      
    #luf=getLDAPPlugin()._getLDAPUserFolder()
    #luf.manage_addServer(host=server.server,
    #                     port=server.port,
    #                     use_ssl=server.connection_type,
    #                     conn_timeout=server.connection_timeout,
    #                     op_timeout=server.operation_timeout)
    
    
    #luf.manage_edit(
    #    title="Plone Managed LDAP",
    #    login_attr=str(config.schema[config.login_attribute].ldap_name),
    #    uid_attr=str(config.schema[config.userid_attribute].ldap_name),
    #    rdn_attr=str(config.schema[config.rdn_attribute].ldap_name),
    #    users_base=config.user_base or "",
    #    users_scope=config.user_scope,
    #    groups_base=config.group_base or "",
    #    groups_scope=config.group_scope,
    #    binduid=str(config.bind_dn) or "",
    #    bindpwd=str(config.bind_password) or "",
    #    roles="Member",
    #    obj_classes=config.user_object_classes)


