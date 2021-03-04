#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  16_get_boards.py - obtain/display the Agile boards a user has access to
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

PROJECT_KEY = 'AGL'  # or TST, JEST, JESTRT, NAVKIT, ...

"""
to get all Agile boards   -  GET /rest/agile/1.0/board

Returns all boards. This only includes boards that the user has permission to view.

Request
QUERY PARAMETERS
parameter	    type	  description
-------------   -------   -----------------------------------------------------------------------
startAt	        long      The starting index of the returned boards. Base index: 0. 
                          See the 'Pagination' section at the top of this page for more details.

maxResults	    int       The maximum number of boards to return per page. 
                          Default: 50. See the 'Pagination' section at the top of this page for more details.

type	        string    Filters results to boards of the specified type. Valid values: scrum, kanban.

name	        string    Filters results to boards that match or partially match the specified name.

projectKeyOrId	string    Filters results to boards that are relevant to a project. 
                          Relevance meaning that the jql filter defined in board contains a reference to a project.
"""
##########################################################################################

def main(args):
    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    boards = jira.getAgileBoards()
    print("\n")
    print(f'{"BoardID":>7} {"Board Name":<24} {"Type":<5}  Board URL')

    for board in boards:
        print(f'{board.id:>7} {board.name:<24.24} {board.type:<5}  {board.url}')

    print(f"\n\n Boards for a specific project: {PROJECT_KEY} ....\n")
    boards = jira.getAgileBoards(PROJECT_KEY)
    print(f'{"BoardID":>7} {"Board Name":<24} {"Type":<5}  Board URL')
    for board in boards:
        print(f'{board.id:>7} {board.name:<24.24} {board.type:<5}  {board.url}')

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])
