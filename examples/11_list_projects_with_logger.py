#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  11_list_projects_with_logger.py - supply a logger instance to the JiraProxy
#                                    get a list of projects and obsever the log file afterwards
#
##########################################################################################

import sys
sys.path.append('/Users/lehki03/projects/jirpa/test')

from jirpa  import JiraProxy, JiraProxyError
from helper_pak import BasicLogger

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
    config = JIRA_REGULAR_USER_CONFIG
    config['logger'] = BasicLogger('11_gp.log')

    jira = JiraProxy(config)

    jira_proj = jira.getProjects()

    print(f'{"Key":<12}  {"Name":<24}' )
    print( "-" * 40)

    for key, name in jira_proj.items():
        print(f'{key:<12}  {name:}')

    print("\n\n")

    jira_project_details = jira.getProjectsDetails()

    print(f'{"Key":<12}  {"Name":<24}  {"ID":<6}' )
    print( "-" * 60)
    for project in jira_project_details:
        print(f'{project["Key"]:<12}  {project["Name"]:<24}  {project["Details"]["id"]:<6}' )


##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])

