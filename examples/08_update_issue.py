#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  08_update_issue.py - create and then update a Jira Issue in the JEST project
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

    ## Create Issue
    issue_attributes = {
        "Summary"     :  "Create Example",
        "Description" :  "A Bug at Creation.",
        "Priority"    :  "High",
        "Fix Version/s" :  "cherry"
       }

    print(f'{"Key":<10} : {"Description":<20} : {"Created":<23} : {"Updated":<23}')
    print("-" * 90)

    issue_key = jira.createIssue(PROJECT_KEY, "Bug", issue_attributes) # returns an issue key
    issue = jira.getIssue(issue_key)
    desc, created, updated = [issue[attr_name] for attr_name in ["Description", "Created", "Updated"]]
    print(f'{issue_key:<10} : {desc:<20} : {created:<23.23} : {updated:<23.23}')

    time.sleep(1)

    issue["Description"] = "A Bug at Update 1"
    jira.updateIssue(issue)

    issue = jira.getIssue(issue_key)
    desc, created, updated = [issue[attr_name] for attr_name in ["Description", "Created", "Updated"]]
    print(f'{issue_key:<10} : {desc:<20} : {created:<23.23} : {updated:<23.23}')

    #print(issue.brief())


##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)

