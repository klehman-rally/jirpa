
import sys, os
import py
import re

from jirpa import JiraProxy, JiraProxyError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG
from jira_targets import PROJECT_KEY_1, PROJECT_NAME_1
from jira_targets import BAD_PROJECT_KEY_1

###############################################################################################

def test_get_permissions_associated_with_project_key():
    """
        will return permissions for a user in a project
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    permissions = jp.getPermissions(PROJECT_KEY_1)

    assert permissions is not None
    assert len(permissions) > 3
    assert 'EDIT_ISSUE'    in permissions
    assert 'CREATE_ISSUE'  in permissions
    assert 'RESOLVE_ISSUE' in permissions


def test_get_permissions_associated_with_project_name():
    """
        will return permissions for a user for a project identified by project name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    permissions = jp.getPermissions(PROJECT_NAME_1)

    assert permissions is not None
    assert len(permissions) > 3
    assert 'EDIT_ISSUE'    in permissions
    assert 'CREATE_ISSUE'  in permissions
    assert 'RESOLVE_ISSUE' in permissions


def test_raise_error_for_bad_project():
    """
        will raise JiraProxyError when project does not exist
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    with py.test.raises(JiraProxyError) as excinfo:
        issue_key = jp.getPermissions(BAD_PROJECT_KEY_1)
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Could not find project for identifier:' in actualErrorMessage


