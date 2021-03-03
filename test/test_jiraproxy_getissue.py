
import sys, os
import py
import re
import copy
from datetime import datetime

from jirpa import JiraProxy, JiraProxyError
from jirpa import JiraFieldSchema
from jirpa import JiraIssueError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG, GOOD_VANILLA_SERVER_DEV_USER_CONFIG 
from jira_targets import PROJECT_KEY_1, PROJECT_NAME_1, PROJECT_DESC_1
#from jira_targets import BAD_PROJECT_KEY_1
#from jira_targets import USER1_USER_NAME, USER1_EMAIL, USER1_ACTIVE
from jira_targets import JEST_ISSUE_1_KEY, JEST_ISSUE_1_RALLY_ITEM, JEST_ISSUE_1_COMMENT
from jira_targets import JEST_BUG_1


LOG_FILE_NAME   = "sedimentary.log"

###############################################################################################

def test_simple_get_issue():
    """
        will return a JiraIssue from a getIssue call
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jira_issue = jp.getIssue(JEST_ISSUE_1_KEY)
    assert jira_issue.key == JEST_ISSUE_1_KEY


def test_get_bug():
    """
        get a bug from a getIssue call
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jira_issue = jp.getIssue(JEST_BUG_1)
    assert jira_issue.key == "JEST-10012"
    # typical timestamp "2018-03-09T14:12:00.000-0700"
    timestamp_patt = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}-\d{4}')
    assert timestamp_patt.search(jira_issue['Support Review Date']) is not None


def test_sad_get_nonexistent_issue():
    """
        will raise StandardError when  getIssue is called with non existent issue
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    
    with py.test.raises(JiraProxyError) as excinfo:
        jira_issue = jp.getIssue("JEST-1001")
    actualErrorMessage = excErrorMessage(excinfo)
    assert "Issue Does Not Exist" in actualErrorMessage


def test_accessing_standard_fields():
    """
        will use both . notation and [] notation to retrieve issue standard field values
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jira_issue = jp.getIssue(JEST_ISSUE_1_KEY)

    assert jira_issue.Reporter    == GOOD_VANILLA_SERVER_CONFIG['user']
    assert jira_issue['Reporter'] == GOOD_VANILLA_SERVER_CONFIG['user']


def test_get_specific_issue_and_fields():
    """
        retrieve issue JEST-23 standard field values
    """
    conf = GOOD_VANILLA_SERVER_DEV_USER_CONFIG
    jp = JiraProxy(conf)
    jira_issue = jp.getIssue("JEST-23")

    assert jira_issue.Reporter    == conf['user']
    assert jira_issue['Reporter'] == conf['user']


def test_accessing_custom_fields():
    """
        will use both . notation and [] notation to retrieve issue custom field values
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jira_issue = jp.getIssue(JEST_ISSUE_1_KEY)

    assert jira_issue.RallyItem    == JEST_ISSUE_1_RALLY_ITEM
    assert jira_issue['RallyItem'] == JEST_ISSUE_1_RALLY_ITEM


def test_issue_creation_with_multiple_versions():
    """
        create a JIRA issue with two version values
    """
    #ZLOG = "zebra.log"
    #logger = BasicLogger(ZLOG)
    #logger.level = 'DEBUG'
    #conf = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    #conf['logger'] = logger
    #jp = JiraProxy(conf)

    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    work_item = {'Summary'   : "stuck vontracular relay caused moribundal shudders " +\
                               "while accelerative mode shunt activated",
                 'Reporter'  : "testuser",
                 'Assignee'  : "devuser",
                 'Description' : "ice blocks whizzed dangerously close to several portholes",
                 'Affects Version/s' : "vanilla",
                 'Fix Version/s' : "cherry, peach",
                }

    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)

    assert issue["Affects Version/s"] == ["vanilla"]
    assert issue["Fix Version/s"]     == ["cherry", "peach"]


def test_get_issue_comment():
    """
        get an issue comment through the getIssue method.
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    issue = jp.getIssue(JEST_ISSUE_1_KEY)
    first_comment = issue.Comment["comments"][0]
    assert first_comment["body"] == JEST_ISSUE_1_COMMENT


def test_get_issue_to_access_custom_datetime_field():
    """
        retrieve issue HIL-16 to observe custom datetime value
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jira_issue = jp.getIssue("HIL-16")
    print(jira_issue['support review date'])
    custom_datetime_patt = re.compile( r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}(\+|-)\d{4,}$')
    assert custom_datetime_patt.match(jira_issue['support review date']) is not None


