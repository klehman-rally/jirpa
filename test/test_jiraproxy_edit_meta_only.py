
import sys, os
import py
import re
import copy

from jirpa import JiraProxy, JiraProxyError
from jirpa import JiraFieldSchema
from jirpa import JiraIssueError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG
from jira_targets import PROJECT_KEY_3

###############################################################################################

def test_get_issue_using_field_in_edit_schema():
    """
        should get a JIRA issue in a project that has a custom field that can 
        only be set by editing, not during creation
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = { "Summary"     :  "Smokey Chess Night",
                  "Reporter"    :  "testuser",
                  "Assignee"    :  "testuser",
                  "Description" :  "Smoke if you got them."
                }
    issue_key = jp.createIssue(PROJECT_KEY_3, "Bug", work_item)

    issue_key_patt = re.compile(f'^{PROJECT_KEY_3}-\\d+')
    assert issue_key_patt.search(issue_key)

    jira_issue = jp.getIssue(issue_key)
    assert jira_issue is not None

    jp.deleteIssue(issue_key)


