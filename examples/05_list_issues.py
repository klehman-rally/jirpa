#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  05_list_issues.py - retrieve the issues for specific Jira project
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

SIMPLE_PROJECT_QUERY    = "project = JEST"
PROJECT_AND_TYPE_QUERY  = "project = JEST AND type = Story ORDER BY key ASC"

##########################################################################################

def main(args):

    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    if not jira:
        print("Unable to obtain a JiraProxy instance for the given configuration")
        sys.exit(1)

    try:
        issues = jira.getIssuesWithJql(SIMPLE_PROJECT_QUERY)
        list_issues(issues)
    except Exception as exc:
        problem = exc.args[0]
        print(f'Error while attempting to retrieve Jira issues: {problem}')
        sys.exit(2)

    print("-" * 80)
    
    try:
        issues = jira.getIssuesWithJql(PROJECT_AND_TYPE_QUERY)
        list_issues(issues)
    except Exception as exc:
        problem = exc.args[0]
        print(f'Error while attempting to retrieve Jira issues: {problem}')
        sys.exit(3)

def list_issues(issues):
    """
    """
    print("\n\n")
    print(f'{"Index":<5} : {"Issue Key":<10} : {"Type":<8} : {"Summary"}')
    print("-" * 60)
    for ix, issue in enumerate(issues[:10]):
        print(f' {ix+1:>4} : {issue.key:<10} : {issue.issue_type:<8} : {issue.Summary}')

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)

