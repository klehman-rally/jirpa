
import sys, os
import py
import re
import copy
import time
from datetime import datetime

from jirpa import JiraProxy, JiraProxyError
from jirpa import JiraIssue

###############################################################################################

#from helper_pak import BasicLogger, excErrorMessage   # shouldn't need these...

from jira_targets import GOOD_VANILLA_SERVER_CONFIG, GOOD_VANILLA_SERVER_DEV_USER_CONFIG 
from jira_targets import PROJECT_KEY_1

###############################################################################################

"""
    Query for Jira issues using jql
"""

proj1 = f'project = {PROJECT_KEY_1}'

def test_simple_query_with_multiple_items():
    """
        will return an Array of JiraIssue objects from a getIssuesWithJql call
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql = f'{proj1} AND issuetype = Story'
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) >= 5
    assert jira_issues[0].__class__ == JiraIssue

def test_query_using_display_name_for_affects_versions():
    """
        will return issues using jql that uses the display name for Affects Version/s
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql =  f'{proj1} AND issuetype = Story AND Affects Version/s = peach'
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0
    assert "peach" in jira_issues[0]["Affects Version/s"]

def test_query_using_display_name_for_components():
    """
        will return issues using jql that uses the display name for Component/s
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql = f'{proj1} AND issuetype = Story AND Component/s = "Front End" '
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0
    assert "Front End" in jira_issues[0]["Component/s"]

def test_query_using_components_with_ampersand_in_value():
    """
        will return issues using jql that for Component/s that use & in their name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql = f'{proj1} AND Component/s = "Sun & Moon" '
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0
    assert "Sun & Moon" in jira_issues[0]["Component/s"]

def test_query_using_components_with_question_mark_in_value():
    """
        will return issues using jql that for Component/s that use ? in their name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql =  f'{proj1} AND Component/s = "Tallest?" '
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0
    assert "Tallest?" in jira_issues[0]["Component/s"]

def test_query_using_components_with_percent_symbol_in_value():
    """
        will return issues using jql that for Component/s that use % in their name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql = f'{proj1} AND Component/s = "machine % calc" '
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0
    assert "machine % calc" in jira_issues[0]["Component/s"]

def disable_test_query_using_components_with_hash_symbol_in_value():
    """
    it 'will return issues using jql that for Component/s that use # in their name' do

        NB:  '#' is a reserved character in Jira JQL.  You cannot effectively escape it
             in Jira in Jira 8.
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    #jql = f'{proj1} AND Component/s = "hash \\#1"'
    jql = f'{proj1} AND Component/s ~ "hash"'
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0
    assert "hash #1" in jira_issues[0]["Component/s"]

def test_query_using_components_with_plus_symbol_in_value():
    """
    it 'will return issues using jql that for Component/s that use + in their name' do
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql = f'{proj1} AND Component/s = "blue + gold" '
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0
    assert "blue + gold" in jira_issues[0]["Component/s"]

def test_query_using_display_name_for_fix_versions():
    """
        will return issues using jql that uses the display name for Fix Version/s
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql = f'{proj1} AND issuetype = Story AND Fix Version/s = lemon'
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0
    assert 'lemon' in jira_issues[0]["Fix Version/s"]

def test_query_using_display_name_for_due_date():
    """
        will return issues using jql that uses the display name for Due Date
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql = f'{proj1} AND issuetype = Story AND Due Date < now()'
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0

def test_query_using_display_name_for_original_estimate():
    """
        will return issues using jql that uses the display name for Original Estimate
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql = f'{proj1} AND issuetype = Story AND Original Estimate > 1h'
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0

def test_query_using_display_name_for_remaining_estimate():
    """
        will return issues using jql that uses the display name for Remaining Estimate
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jql = f'{proj1} AND issuetype = Story AND Remaining Estimate > 1h'
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0

def test_query_specifying_for_field_not_having_null_value():
    """
        will return issues using jql when a field is specified as not having a null value
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    #status != Closed and component != "Starboard Foot"
    #jql  = f'proj1} AND Component/s != "Starboard Foot" AND "Affects Version" != null'
    jql  = f'{proj1} AND Component/s != "Starboard Foot" AND status != Closed'
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0

def test_query_specifying_for_field_whose_value_is_null():
    """
        query using jql for issues having no value in a specific field
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    jql  = f'{proj1} AND status != Closed AND assignee is null'
    jira_issues = jp.getIssuesWithJql(jql)
    assert len(jira_issues) > 0

