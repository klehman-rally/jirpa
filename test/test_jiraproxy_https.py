
import sys, os
import re
import py

from jirpa import JiraProxy, JiraProxyError

from jira_targets import GOOD_VANILLA_ONDEMAND_REGULAR_USER_CONFIG
from jira_targets import PROJECT_KEY_1

#################################################################################

def test_get_on_demand_connection():
    """
        will obtain a JiraProxy instance using https
    """
    jp = JiraProxy(GOOD_VANILLA_ONDEMAND_REGULAR_USER_CONFIG)
    assert jp is not None
    assert jp.jira_version is not None
    assert len(jp.status_values) > 3


def test_create_new_issue_via_on_demand_connection():
    """
        create a minimal JIRA issue via the createIssue method over https
    """
    jp = JiraProxy(GOOD_VANILLA_ONDEMAND_REGULAR_USER_CONFIG)
    work_item = {"Summary" : "kindergarten hopscotch games"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue_key_patt = re.compile(f'{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.search(issue_key) is not None

    jp.deleteIssue(issue_key)


