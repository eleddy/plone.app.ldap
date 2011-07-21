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

    servers = {}
    
    # these are really just default values
    _ldap_type = u"LDAP"
    _bind_dn = ""
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
    _rdn_attribute = "uid"
    _userid_attribute = "uid"
    _login_attribute = "uid"
    _user_object_classes = "pilotPerson"

    
    _luf = None

    """
    XXX: when should we flush the cache? when the form is submitted?
    
    TODO: To display forms, having a pas plugin is not required. To
    edit them, however, it is. Currently this is assumed to be 
    done in controlpanel.py before these setters are hit. 
    
    XXX: need to get the values from the back end if they exist 
    but there is the issue
    
    XXX: Currently can't remove bind dn
    
    XXX: maybe just have a decorator which requires luf to exist?
    """ 
    
    def getUser_object_classes(self):
        return self._user_object_classes
    
    def setUser_object_classes(self, value):
        self._user_object_classes = value
        if self.luf:
            self.luf.setObject_classes(value)
    
    def getLogin_attribute(self):
        return self._login_attribute
    
    def setLogin_attribute(self, value):
        self._login_attribute = value
        if self.luf:
            self.luf.setLogin_attr(value)
    
    def getUserid_attribute(self):
        return self._userid_attribute
    
    def setUserid_attribute(self, value):
        self._userid_attribute = value
        if self.luf:
            self.luf.setUid_attr(value)
    
    def getCache(self):
        return self._cache
    
    def setCache(self, value):
        self._cache = value
        
    def getActivated_plugins(self):
        return self._activated_plugins
    
    def setActivated_plugins(self, value):
        self._activated_plugins = value
    
    def getActivated_interfaces(self):
        return self._activated_interfaces
    
    def setActivated_interfaces(self, value):
        self._activated_interfaces = value    
    
    def getDefault_user_roles(self):
        return self._default_user_roles
    
    def setDefault_user_roles(self, value):
        self._default_user_roles = value
        if self.luf:
            self.luf.setRoles(value)
    
    def getPassword_encryption(self):
        return self._password_encryption
    
    def setPassword_encryption(self, value):
        self._password_encryption = value
        if self.luf:
            self.luf.setEncryption(value)
        
    def getGroup_scope(self):
        return self._group_scope
    
    def setGroup_scope(self, value):
        self._group_scope = value
        if self.luf:
            self.luf.setGroups_scope(value)
        
    def getGroup_base(self):
        return self._group_base
    
    def setGroup_base(self, value):
        self._group_base = value
        if self.luf:
            self.luf.setGroups_base(value)
    
    def getUser_scope(self):
        return self._user_scope
    
    def setUser_scope(self, value):
        self._user_scope = value
        if self.luf:
            self.luf.setUsers_scope(value)
    
    def getUser_base(self):
        return self._user_base
        
    def setUser_base(self, value):
        self._user_base = value
        if self.luf:
            self.luf.setUsers_base(value)
    
    def getBind_password(self):
        return self._bind_password
        
    def setBind_password(self, value):
        self._bind_password = value
        if self.luf:
            self.luf.setBindpwd(value)
   
    def getRdn_attribute(self):
        return self._rdn_attribute
        
    def setRdn_attribute(self, value):
        self._rdn_attribute = value
        if self.luf:
            self.luf.setRdn_attr(value)
    
    def getLdap_type(self):
        return self._ldap_type
    
    def setLdap_type(self, value):
        # TODO: if we update the type, need to recreate the plugin
        # XXX: 
        self._ldap_type = value
    
    def getBind_dn(self):
        return self._bind_dn
    
    def setBind_dn(self, value):
        self._bind_dn = value
                    
        if self.luf:
            self.luf.setBinduid(value)
    
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
        
    user_object_classes = property(getUser_object_classes, setUser_object_classes)
    login_attribute = property(getLogin_attribute, setLogin_attribute)
    userid_attribute = property(getUserid_attribute, setUserid_attribute)
    cache = property(getCache, setCache)
    activated_plugins = property(getActivated_plugins, setActivated_plugins)
    activated_interfaces = property(getActivated_interfaces, setActivated_interfaces)
    default_user_roles = property(getDefault_user_roles, setDefault_user_roles)
    password_encryption = property(getPassword_encryption, setPassword_encryption)
    group_scope = property(getGroup_scope, setGroup_scope)
    group_base = property(getGroup_base, setGroup_base)
    user_scope = property(getUser_scope, setUser_scope)
    user_base = property(getUser_base, setUser_base)
    bind_password = property(getBind_password, setBind_password)
    rdn_attribute = property(getRdn_attribute, setRdn_attribute)
    ldap_type = property(getLdap_type, setLdap_type)
    bind_dn = property(getBind_dn, setBind_dn)

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


