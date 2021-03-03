#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  12_show_story_fields.py - display the standard fields for a Storyn in a specific project
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

##########################################################################################

def main(args):
    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    project_key, issue_type = "TST", "Story"
    print(f'\n Project: {project_key}   Issue type: {issue_type}')
    print("   Fields\n   ---------------")

    for field_name in jira.getStandardFields(project_key, issue_type):
        print( f"   {field_name}")
    print("")

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])


