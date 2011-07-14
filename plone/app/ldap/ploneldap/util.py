from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.interface import directlyProvides
from plone.app.ldap.engine.interfaces import ILDAPConfiguration
from Products.CMFCore.utils import getToolByName
from Products.PloneLDAP.plugins.ad import PloneActiveDirectoryMultiPlugin
from Products.PloneLDAP.plugins.ldap import PloneLDAPMultiPlugin
from Products.PloneLDAP.factory import genericPluginCreation
from plone.app.ldap.ploneldap.interfaces import IManagedLDAPPlugin


def getPAS():
    site=getSite()
    return getToolByName(site, "acl_users")

def lookupLDAPPlugin():
    """
    Return the ldap plugin, or None if it does not exist
    """
    pas=getPAS()
    for plugin in pas.objectValues([PloneActiveDirectoryMultiPlugin.meta_type,
                                    PloneLDAPMultiPlugin.meta_type]):
        if IManagedLDAPPlugin.providedBy(plugin):
            return plugin

    return None
    
def validLDAPTypeConfiguration(plugin):
    """
    If the type for an ldap plugin changes from AD to LDAP 
    or vice versa, we need to recreate the plugin.
    
    Return True if the current plugin has the same meta type 
    as the configuration states. False if there is no plugin,
    or if the configuration is inconsistent.
    """
    ldap_meta_type_map = {
        PloneActiveDirectoryMultiPlugin.meta_type : u"AD",
        PloneLDAPMultiPlugin.meta_type : u"LDAP",
        }
    
    config=getUtility(ILDAPConfiguration)
    
    if plugin and ldap_meta_type_map[plugin.meta_type] != config.ldap_type:
        return False
    
    return True
    
    
def updateLDAPType(plugin):
    """
    If the LDAP type is changed, we need to recreate the plugin for 
    that type under the new type. If updated, return True, If 
    the weather is clear, do nothing and return False
    """
    if plugin and not validLDAPTypeConfiguration(plugin):
        pas=getPAS()
        id = plugin.getId()
        pas.manage_delObjects([plugin.getId()])         
        createPluginFromConfig(id)
        return True
    
    return False



def getLDAPPlugin():
    ''' backwords compat at the moment '''
    plugin = lookupLDAPPlugin()
    if not plugin:
        raise KeyError
 
    if updateLDAPType(plugin): # new plugin made
        plugin = lookupLDAPPlugin()
    
    return plugin 


def guarunteeAndGetLDAPPlugin():
    """
    Return the existing ldap plugin, or create on if it doesn't
    already exist.
    
    If a plugin exists but is of the wrong type, delete the wrong 
    type and create a new one.
    """
    
    plugin = lookupLDAPPlugin()
    if plugin: 
        if updateLDAPType(plugin): # new plugin made
            plugin = lookupLDAPPlugin()
    else:            
        plugin = createPluginFromConfig()
    
    return plugin   


def createPluginFromConfig(id="ldap-plugin"):
    """
    Create a new plugin based on the global config at 
    ILDAPConfiguration
    """
    createLDAPPlugin(id)
    configureLDAPServers()
    configureLDAPSchema()    


def createLDAPPlugin(id="ldap-plugin"):
    """
    Create an ldap plugin based on global configuration
    """
    pas=getPAS()
    config=getUtility(ILDAPConfiguration)
    if config.ldap_type==u"AD":
        klass=PloneActiveDirectoryMultiPlugin
    else:
        klass=PloneLDAPMultiPlugin

    genericPluginCreation(pas, klass, 
            id=id,
            title="Plone managed LDAP",
            login_attr=str(config.schema[config.login_attribute].ldap_name),
            uid_attr=str(config.schema[config.userid_attribute].ldap_name),
            rdn_attr=str(config.schema[config.rdn_attribute].ldap_name),
            users_base=config.user_base or "",
            users_scope=config.user_scope,
            groups_base=config.group_base or "",
            groups_scope=config.group_scope,
            binduid=config.bind_dn or "",
            bindpwd=config.bind_password or "",
            encryption=config.password_encryption,
            roles=config.default_user_roles or "",
            obj_classes=config.user_object_classes)

    plugin=getattr(pas, id)
    plugin.groupid_attr="cn"
    directlyProvides(plugin, IManagedLDAPPlugin)
    enablePASInterfaces()
    enableCaching(config.cache)
    return plugin


def configureLDAPServers():
    luf=getLDAPPlugin()._getLDAPUserFolder()
    config=getUtility(ILDAPConfiguration)

    luf.manage_deleteServers(range(len(luf.getServers())))
    for server in config.servers.values():
        if server.enabled:
            luf.manage_addServer(host=server.server,
                                 port=server.port,
                                 use_ssl=server.connection_type,
                                 conn_timeout=server.connection_timeout,
                                 op_timeout=server.operation_timeout)


def addMandatorySchemaItems():
    luf=getLDAPPlugin()._getLDAPUserFolder()
    config=getUtility(ILDAPConfiguration)

    if config.ldap_type==u"AD":
        required = [ ("dn", "Distinguished Name"),
                     ("objectGUID", "AD Object GUID"),
                     ("cn", "Canonical Name"),
                     ("memberOf", "Group DNs", True, "memberOf")]
    else:
        required = []

    schema=luf.getSchemaConfig()
    for prop in required:
        if prop[0] not in schema:
            luf.manage_addLDAPSchemaItem(*prop)


def configureLDAPSchema():
    luf=getLDAPPlugin()._getLDAPUserFolder()
    config=getUtility(ILDAPConfiguration)

    schema={}
    for property in config.schema.values():
        schema[str(property.ldap_name)]=dict(
                ldap_name=str(property.ldap_name),
                friendly_name=property.description,
                public_name=str(property.plone_name),
                multivalued=property.multi_valued)
    luf.setSchemaConfig(schema)
    addMandatorySchemaItems()


def enablePASInterfaces():
    plugin=getLDAPPlugin()
    config=getUtility(ILDAPConfiguration)

    common_interfaces = [
            'IUserEnumerationPlugin',
            'IGroupsPlugin',
            'IGroupEnumerationPlugin',
            'IRoleEnumerationPlugin',
            'IAuthenticationPlugin',
            'ICredentialsResetPlugin',
            'IPropertiesPlugin',
            'IRolesPlugin',
            'IGroupIntrospection',
            ]

    ldap_interfaces = common_interfaces + [
            'IGroupManagement',
            'IUserAdderPlugin',
            'IUserManagement',
            ]

    ad_interfaces = common_interfaces
    
    if config.activated_plugins:
        plugin.manage_activateInterfaces(config.activated_plugins)
    else:
        if config.ldap_type==u"AD":
            plugin.manage_activateInterfaces(ad_interfaces)
        else:
            plugin.manage_activateInterfaces(ldap_interfaces)
            
    
    if config.ldap_type != u"AD":
        plugins=getPAS().plugins
    
        iface=plugins._getInterfaceFromName("IUserAdderPlugin")
        for i in range(len(plugins.listPlugins(iface))-1):
            plugins.movePluginsUp(iface, [plugin.getId()])
    
        iface=plugins._getInterfaceFromName("IPropertiesPlugin")
        for i in range(len(plugins.listPlugins(iface))-1):
            plugins.movePluginsUp(iface, [plugin.getId()])


def enableCaching(cache_manager="RAMCache"):
    pas=getPAS()
    if pas.ZCacheable_getManager() is None:
        pas.ZCacheable_setManagerId(manager_id=cache_manager)
    getLDAPPlugin().ZCacheable_setManagerId(manager_id=cache_manager)



# XXX: This may get removed
def guaranteePluginExists():
    """Make sure a proper PAS plugin exists.

    If a plugin exists but it is of the wrong type (AD vs standard LDAP)
    the plugin is removed and a new one is created.

    If a new plugin has been created True is returned. If there was
    a valid plugin present False is returned.
    """
    config=getUtility(ILDAPConfiguration)
    plugin=getLDAPPlugin()
    if plugin:
        if plugin.meta_type==PloneActiveDirectoryMultiPlugin.meta_type and \
            config.ldap_type==u"AD":
            return False
        if plugin.meta_type==PloneLDAPMultiPlugin.meta_type and \
            config.ldap_type==u"LDAP":
            return False
             
        # There is a managed plugin, but it is of the wrong type.
        pas=getPAS()
        pas.manage_delObjects([plugin.getId()])

    createLDAPPlugin()
    configureLDAPServers()
    configureLDAPSchema()
    return True
