#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  04_list_jira_projects.py - retrieve names of projects a user has access to 
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
        jira_projects = jira.getProjects()
    except Exception as exc:
        problem = exc.args[0]
        print(f'Error while attempting to retrieve Jira project names: {problem}')
        sys.exit(2)
    
    for key in jira_projects:
        print(key)
    print("\n")

    try:
        jira_project_details = jira.getProjectsDetails()
    except Exception as exc:
        problem = exc.args[0]
        print(f'Error while attempting to retrieve Jira project details: {problem}')
        sys.exit(3)

    print(f'{"Key":<12}  :  {"Name":<30}  :  {"ID":<6}')        
    print("-" * 60)

    for project in jira_project_details:
        key, name, details = [project[attr] for attr in ['Key', 'Name', 'Details']]
        print(f'{key:<12}  :  {name:<30}  : {details["id"]:>6}')
    print("\n")


##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)

