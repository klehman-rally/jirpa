#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  09_show_users.py - retrieve and show all users for the target Jira instance
#
##########################################################################################

import sys
import time

from jirpa  import JiraProxy, JiraProxyError

##########################################################################################

SERVER_INSTANCE = "http://10.23.22.11:8080" # int-hobart in GCP saas-rally-dev-integrations

JIRA_REGULAR_USER_CONFIG = \
    {
     'user'       :  "testuser",
     'password'   :  "jiradev",
     'url'        :  SERVER_INSTANCE
    }

PROJECT_KEY = 'JEST'

##########################################################################################

def main(args):

    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    users = jira.getAllUsers()
    for user in users:
        print(user.info())
        #print(user)

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)


