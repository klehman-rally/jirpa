#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  13_project_permissions.py - show the permissions a user does have and that they
#                              don't have in a specific project
#
##########################################################################################

import sys

from jirpa  import JiraProxy, JiraProxyError

##########################################################################################

SERVER_INSTANCE = "http://10.23.22.11:8080" # int-hobart in GCP saas-rally-dev-integrations

JIRA_REGULAR_USER_CONFIG = \
    {
     'user'       :  "testuser",
     'password'   :  "jiradev",
     'url'        :  SERVER_INSTANCE
    }

PROJECT_KEY = "JEST"

##########################################################################################

def main(args):
    config = JIRA_REGULAR_USER_CONFIG
    jira = JiraProxy(config)

    permissions = jira.getPermissions(PROJECT_KEY)
    permission_keys = sorted(permissions.keys())

    #each permission value has id, key, name, description, and havePermission attributes
    have_permissions = [ key for key, perm in permissions.items() if     perm['havePermission'] ]
    lack_permissions = [ key for key, perm in permissions.items() if not perm['havePermission'] ]
    #have_permissions = permissions.collect{|name, permission| permission}
    #                              .select{|p|  p['havePermission']}
    #lack_permissions = permissions.collect{|name, permission| permission}
    #                              .select{|p| !p['havePermission']}

    print( "")
    print( f"In {config['url']} the login user {config['user']} \n"
           f"HAS   these permissions for the project: {PROJECT_KEY}")
    for perm_key in permission_keys:
        if perm_key in have_permissions:
            perm_name = permissions[perm_key]['name']
            print( f"{perm_key:<32.32}   {perm_name}") 

    print( "\n\n")

    print( f"In {config['url']} the login user {config['user']} \n"
           f"LACKS these permissions for the project: {PROJECT_KEY}")
    for perm_key in permission_keys:
        if perm_key in lack_permissions:
            perm_name = permissions[perm_key]['name']
            print( f"{perm_key:<32.32}   {perm_name}") 
    print( "")

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])


