#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  03_jira_info.py - retrieve basic server info for an Atlassian Jira instance
#
##########################################################################################

import sys

from jirpa  import JiraProxy, JiraProxyError

##########################################################################################

SERVER_INSTANCE   = "http://10.23.22.11:8080"

JIRA_REGULAR_USER_CONFIG = \
    {
     'user'       :  "testuser",
     'password'   :  "jiradev",
     'url'        :  SERVER_INSTANCE
    }

##########################################################################################

def main(args):

    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    if not jira:
        print("Unable to obtain a JiraProxy instance for the given configuration")
        sys.exit(1)

    try:
        jira_info = jira.getServerInfo()

        print(f"Jira Server URL: {jira_info.url}")
        print(f"Jira Server Version: {jira_info.version}")
    except Exception as exc:
        problem = exc.args[0]
        print(f'Error while attempting to retrieve Jira server info: {problem}')
        sys.exit(2)

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)
