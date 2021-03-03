#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  07_create_issue.py - create a Jira Issue in the JEST project
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

PROJECT_KEY = 'JEST'

##########################################################################################

def main(args):

    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    ## Create Issue
    issue_attributes = {
      "Summary"       :  "Before Genesis was a primal swamp",
      "Description"   :  "Methusalah's hexta-grandfather was there and told of chaoas",
      "Priority"      :  "Medium",   # tried this but no go ....  "Trivial",
      "Fix Version/s" :  "cherry"
    }
    issue_key = jira.createIssue(PROJECT_KEY, "Bug", issue_attributes) # returns an issue key

    issue = jira.getIssue(issue_key)
    status = issue.status
    print(f"Issue : {issue.key}")
    print(issue.brief())
    print("")
    print("-" * 60)
    print(f'{"Key":<20} : {"Value"}')
    print("---------------    ----------")
    values = issue.attributeValues()
    for attribute_name, value in values:
        print(f'{attribute_name:<20} : {value}')
    print("")


##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)


