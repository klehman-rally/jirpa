
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
from jira_targets import BAD_PROJECT_KEY_1
from jira_targets import DESIGNATED_ACTIVE_USER, DESIGNATED_INACTIVE_USER
from jira_targets import USERNUM_USER_NAME, USERNUM_DISPLAY_NAME, USERNUM_EMAIL, USERNUM_ACTIVE

###############################################################################################

def test_get_assignable_users():
    """
        will return assignable users with the getAssignableUsers method
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    users = jp.getAssignableUsers(PROJECT_KEY_1)

    assert len(users) > 1
    
    user_names = [user.name for user in users]
    assert GOOD_VANILLA_SERVER_CONFIG['user'] in user_names


def test_get_all_users():
    """
        will return all users with the getAllUsers method
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    users = jp.getAllUsers()

    assert len(users) >= 4

    user_names = [user.name for user in users]
    assert DESIGNATED_ACTIVE_USER   in user_names
    assert DESIGNATED_INACTIVE_USER in user_names

    active_user   = [user for user in users if user.name == DESIGNATED_ACTIVE_USER][0]
    inactive_user = [user for user in users if user.name == DESIGNATED_INACTIVE_USER][0]

    assert active_user.active == True
    assert inactive_user.active == False


def test_get_digity_inactive_user():
    """
        should find an inactive user whose username contains only digits
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    users = jp.getAllUsers()

    jb_user = [u for u in users if u.name == USERNUM_USER_NAME][0]
    assert jb_user.display_name == USERNUM_DISPLAY_NAME


def test_get_jira_user_with_info():
    """
        return a JiraUser with all attributes correctly populated
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    users = jp.getAllUsers()

    jb_user = [u for u in users if u.name == USERNUM_USER_NAME][0]
    assert jb_user.display_name == USERNUM_DISPLAY_NAME
    assert jb_user.email        == USERNUM_EMAIL
    assert jb_user.active       == USERNUM_ACTIVE


def test_valid_project_get_assignable_users():
    """
        will return assignable users with the getAssignableUsers method 
        for a valid project name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    users = jp.getAssignableUsers(PROJECT_NAME_1)

    assert len(users) > 1

    user_names = [user.name for user in users]
    assert GOOD_VANILLA_SERVER_CONFIG['user'] in user_names


def test_sad_raise_for_invalid_project_identifier():
    """
        on attempt to get users will raise an error for a invalid project identifier
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    with py.test.raises(JiraProxyError) as excinfo:
        users = jp.getAssignableUsers(BAD_PROJECT_KEY_1)
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Could not find project for identifier:' in actualErrorMessage


