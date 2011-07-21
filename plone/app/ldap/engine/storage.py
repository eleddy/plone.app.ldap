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


# TODO: rename this to something more meaningful like
# e.g. LDAPConfigurationProxy

class LDAPConfiguration(object):
    implements(ILDAPConfiguration)

    
    userid_attribute = "uid"
    login_attribute = "uid"
    user_object_classes = "pilotPerson"
    
    servers = {}
    
    _ldap_type = u"LDAP"
    _bind_dn = ""
    _rdn_attribute = "uid"
    _bind_password = ""
    _user_base = ""
    _user_scope = SCOPE_SUBTREE
    _group_base = ""
    _group_scope = SCOPE_SUBTREE
    _password_encryption = ""
    _default_user_roles = ""
    _activated_interfaces = []    
    _activated_plugins = None
    _cache = ''

    
    _luf = None

    """
    For the setters, we go through manage because it clears
    the cache in the backend when it updates the attributes.
    Make sure the setter always updates the local config as 
    well so we don't have to check for luf each time.
    
    XXX:This may duplicate a lot of work actually - maybe flushing 
    the cache on form submit is better?
    
    To display forms, having a pas plugin is not required. To
    edit them, however, it is. Currently this is assumed to be 
    done in controlpanel.py before these setters are hit. 
    
    XXX: need to get the values from the back end if they exist 
    but there is the issue
    """ 
    
    def getCache(self):
        return self._cache
    
    def setCache(self, value):
        self._cache = value
    
    cache = property(getCache, setCache)
        
    def getActivated_plugins(self):
        return self._activated_plugins
    
    def setActivated_plugins(self, value):
        self._activated_plugins = value
    
    activated_plugins = property(getActivated_plugins, setActivated_plugins)
    
    def getActivated_interfaces(self):
        return self._activated_interfaces
    
    def setActivated_interfaces(self, value):
        self._activated_interfaces = value
    
    activated_interfaces = property(getActivated_interfaces, setActivated_interfaces)
    
    
    def getDefault_user_roles(self):
        return self._default_user_roles
    
    def setDefault_user_roles(self, value):
        self._default_user_roles = value
    
    default_user_roles = property(getDefault_user_roles, setDefault_user_roles)
    
    def getPassword_encryption(self):
        return self._password_encryption
    
    def setPassword_encryption(self, value):
        self._password_encryption = value
    
    password_encryption = property(getPassword_encryption, setPassword_encryption)
    
    
    def getGroup_scope(self):
        return self._group_scope
    
    def setGroup_scope(self, value):
        self._group_scope = value
    
    group_scope = property(getGroup_scope, setGroup_scope)
    
    
    def getGroup_base(self):
        return self._group_base
    
    def setGroup_base(self, value):
        self._group_base = value
    
    group_base = property(getGroup_base, setGroup_base)
    
    def getUser_scope(self):
        return self._user_scope
    
    def setUser_scope(self, value):
        self._user_scope = value
    
    user_scope = property(getUser_scope, setUser_scope)
    
    def getUser_base(self):
        return self._user_base
        
    def setUser_base(self, value):
        self._user_base = value
    
    user_base = property(getUser_base, setUser_base)
    
    def getBind_password(self):
        return self._bind_password
        
    def setBind_password(self, value):
        self._bind_password = value
    
    bind_password = property(getBind_password, setBind_password)
   
    def getRdn_attribute(self):
        return self._rdn_attribute
        
    def setRdn_attribute(self, value):
        self._rdn_attribute = value
        # XXX: This made things pretty angry!
        #if self.luf:
        #    self.luf.manage_changeProperty('_rdnattr', value)
        
    rdn_attribute = property(getRdn_attribute, setRdn_attribute)
    
    def getLdap_type(self):
        return self._ldap_type
    
    def setLdap_type(self, value):
        # TODO: if we update the type, need to recreate the plugin
        self._ldap_type = value
        
    ldap_type = property(getLdap_type, setLdap_type)
    
    def getBind_dn(self):
        return self._bind_dn
    
    def setBind_dn(self, value):
        '''
        Setting a dn with bad values causes major borkage from the 
        top down. We can use this proxy config to make sure the end 
        user doesn't hate themselves for a silly typo.
        '''
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


