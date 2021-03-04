#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  17_get_sprints.py - obtain/display the sprints defined in an Agile board
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

PROJECT_KEY           = 'AGL'
TARGET_AGILE_BOARD    = 'AGL board'
TARGET_AGILE_BOARD_ID = 1


"""

https://docs.atlassian.com/jira-software/REST/cloud/#agile/1.0/board/{boardId}/sprint-getAllSprints to get all the sprints for a board.


Get all sprints
GET /rest/agile/1.0/board/{boardId}/sprint
Returns all sprints from a board, for a given board Id. This only includes sprints that the user has permission to view.

Request
QUERY PARAMETERS
parameter	type 	 description
---------   -----    ------------------------------------------------------------------
startAt	    long     The starting index of the returned sprints. 
                     Base index: 0. See the 'Pagination' section at the top of this page for more details.

maxResults	int      The maximum number of sprints to return per page. Default: 50. 
                     See the 'Pagination' section at the top of this page for more details.

state	    string   Filters results to sprints in specified states. Valid values: future, active, closed. 
                     You can define multiple states separated by commas, e.g. state=active,closed

Responses
STATUS 200 - application/jsonReturns the requested sprints, at the specified page of the results. 
              Sprints will be ordered first by state (i.e. closed, active, future) 
              then by their position in the backlog.
EXAMPLE
{
    "maxResults": 2,
    "startAt": 1,
    "total": 5,
    "isLast": false,
    "values": [
        {
            "id": 37,
            "self": "http://www.example.com/jira/rest/agile/1.0/sprint/23",
            "state": "closed",
            "name": "sprint 1",
            "startDate": "2015-04-11T15:22:00.000+10:00",
            "endDate": "2015-04-20T01:22:00.000+10:00",
            "completeDate": "2015-04-20T11:04:00.000+10:00",
            "originBoardId": 5
        },
        {
            "id": 72,
            "self": "http://www.example.com/jira/rest/agile/1.0/sprint/73",
            "state": "future",
            "name": "sprint 2"
        }
    ]
}
STATUS 400Returned if the request is invalid.
STATUS 401Returned if the user is not logged in.
STATUS 403Returned if the user does not a have valid license.
STATUS 404Returned if board does not exist or the user does not have permission to view it.
"""

##########################################################################################

def main(args):
    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    sprints = jira.getAgileSprints(PROJECT_KEY, TARGET_AGILE_BOARD)
    print("\n")
    print(f'{"SprintId":>7} {"Sprint Name":<20} {"State":<8}    '
          f'{"Started":<10}  {"Ending":<10}  {"Completed":<10}  Board URL')


    for sprint in sprints:
        start, end, comp = "", "", ""
        if sprint.start_date: start = sprint.start_date
        if sprint.end_date: end = sprint.end_date
        if sprint.complete_date: comp = sprint.complete_date
        print(f' {sprint.id:>7} {sprint.name:<20.20} {sprint.state:<5}    '
              f'{start:<10.10}  {end:<10.10}  {comp:<10.10}    {sprint.url}')

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])

