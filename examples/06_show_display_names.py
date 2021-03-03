#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  06_show_display_names.py - show the field display names for a specific issue
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

ISSUE_KEY = "JEST-138"

##########################################################################################

def main(args):

    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    issue = jira.getIssue(ISSUE_KEY)

    display_names = issue.attributeDisplayNames()
    for name in display_names:
        print(name)

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)

