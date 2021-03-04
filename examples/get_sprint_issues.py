#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  18_get_sprint_issues.py - obtain/display the issues in a specific sprint
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
TARGET_AGILE_BOARD    = 'AGL board' # has
TARGET_AGILE_BOARD_ID = 1


"""
Get issues for sprint
GET /rest/agile/1.0/board/{boardId}/sprint/{sprintId}/issue

Get all issues you have access to that belong to the sprint from the board. 
Issue returned from this resource contains additional fields like: sprint, closedSprints, flagged and epic. 
Issues are returned ordered by rank. JQL order has higher priority than default rank.

Request
QUERY PARAMETERS
parameter	type	description
---------   -----   ----------------------------------------------------------------------
startAt	    long    The starting index of the returned issues. Base index: 0. 
                    See the 'Pagination' section at the top of this page for more details.

maxResults	int     The maximum number of issues to return per page. Default: 50. 
                    See the 'Pagination' section at the top of this page for more details. 
                    Note, the total number of issues returned is limited by the property 'jira.search.views.default.max' in your JIRA instance. If you exceed this limit, your results will be truncated.

jql	        string  Filters results using a JQL query. 
                     If you define an order in your JQL query, 
                     it will override the default order of the returned issues.

validateQuery	boolean   Specifies whether to validate the JQL query or not. Default: true.

fields	    string   The list of fields to return for each issue. 
                     By default, all navigable and Agile fields are returned.

expand	    string   A comma-separated list of the parameters to expand.

Responses
STATUS 200 - application/jsonReturns the requested issues, at the specified page of the results.
EXAMPLE
{
    "expand": "names,schema",
    "startAt": 0,
    "maxResults": 50,
    "total": 1,
    "issues": [
        {
            "expand": "",
            "id": "10001",
            "self": "http://www.example.com/jira/rest/agile/1.0/board/92/issue/10001",
            "key": "HSP-1",
            "fields": {
                "flagged": true,
                "sprint": {
                    "id": 37,
                    "self": "http://www.example.com/jira/rest/agile/1.0/sprint/13",
                    "state": "future",
                    "name": "sprint 2"
                },
                "closedSprints": [
                    {
                        "id": 37,
                        "self": "http://www.example.com/jira/rest/agile/1.0/sprint/23",
                        "state": "closed",
                        "name": "sprint 1",
                        "startDate": "2015-04-11T15:22:00.000+10:00",
                        "endDate": "2015-04-20T01:22:00.000+10:00",
                        "completeDate": "2015-04-20T11:04:00.000+10:00"
                    }
                ],
                "description": "example bug report",
                "project": {
                    "self": "http://www.example.com/jira/rest/api/2/project/EX",
                    "id": "10000",
                    "key": "EX",
                    "name": "Example",
                    "projectCategory": {
                        "self": "http://www.example.com/jira/rest/api/2/projectCategory/10000",
                        "id": "10000",
                        "name": "FIRST",
                        "description": "First Project Category"
                    }
                },
                "epic": {
                    "id": 37,
                    "self": "http://www.example.com/jira/rest/agile/1.0/epic/23",
                    "name": "epic 1",
                    "summary": "epic 1 summary",
                    "color": {
                        "key": "color_4"
                    },
                    "done": true
                },
                "worklog": [
                    {
                        "self": "http://www.example.com/jira/rest/api/2/issue/10010/worklog/10000",
                        "author": {
                            "self": "http://www.example.com/jira/rest/api/2/user?username=fred",
                            "name": "fred",
                            "displayName": "Fred F. User",
                            "active": false
                        },
                        "updateAuthor": {
                            "self": "http://www.example.com/jira/rest/api/2/user?username=fred",
                            "name": "fred",
                            "displayName": "Fred F. User",
                            "active": false
                        },
                        "comment": "I did some work here.",
                        "updated": "2017-02-08T17:08:41.332+0000",
                        "visibility": {
                            "type": "group",
                            "value": "jira-developers"
                        },
                        "started": "2017-02-08T17:08:41.332+0000",
                        "timeSpent": "3h 20m",
                        "timeSpentSeconds": 12000,
                        "id": "100028",
                        "issueId": "10002"
                    }
                ],
                "updated": 1,
                "timetracking": {
                    "originalEstimate": "10m",
                    "remainingEstimate": "3m",
                    "timeSpent": "6m",
                    "originalEstimateSeconds": 600,
                    "remainingEstimateSeconds": 200,
                    "timeSpentSeconds": 400
                }
            }
        }
    ]
}
STATUS 400Returned if the request is invalid.
STATUS 401Returned if the user is not logged in.
STATUS 403Returned if the user does not a have valid license.
STATUS 404Returned if the board does not exist or the user does not have permission to view it.
"""

##########################################################################################

def main(args):
    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    boards = jira.getSprintIssues(board, sprint)
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

