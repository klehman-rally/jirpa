
import sys, os
import py
import re
import copy
from datetime import datetime

from jirpa import JiraProxy, JiraProxyError
from jirpa import JiraFieldSchema

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG
from jira_targets import PROJECT_KEY_1, PROJECT_NAME_1, PROJECT_DESC_1
from jira_targets import BAD_PROJECT_KEY_1
from jira_targets import USER1_USER_NAME, USER1_EMAIL, USER1_ACTIVE

PROJECT_KEY = 'TST'

LOG_FILE_NAME   = "igneous.log"

###############################################################################################



def test_create_bug_with_target_release_value():
    """
        create a new Jira Bug with a valid Target Release value
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    item_data = {'Summary'          : 'Archery nomads on a rampage for doilies', 
                 'Target Release'   : 'lime'
                }
    issue_key = jp.createIssue(PROJECT_KEY, 'Bug', item_data)
    issue = jp.getIssue(issue_key)
    assert issue['Target Release'] == 'lime'

def test_create_bug_with_single_affects_version_value():
    """
        create a new Jira Bug with a single valid Affects Version/s value
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    item_data = {'Summary'            : 'Narrow morbid futons for sales', 
                 'Affects Version/s'  : 'orange'
                }
    issue_key = jp.createIssue(PROJECT_KEY, 'Bug', item_data)
    issue = jp.getIssue(issue_key)
    assert issue['Affects Version/s'] == ['orange']

def test_create_bug_with_multiple_affects_version_values():
    """
        create a new Jira Bug with a multiple valid Affects Version/s values
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    item_data = {'Summary'            : 'Narrow morbid futons for sales', 
                 'Affects Version/s'  : 'apple,lime'
                }
    issue_key = jp.createIssue(PROJECT_KEY, 'Bug', item_data)
    issue = jp.getIssue(issue_key)
    assert issue['Affects Version/s']  == ['apple', 'lime']


