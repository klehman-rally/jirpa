
import sys, os
import py

from jirpa import JiraProxy, JiraProxyError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG
from jira_targets import PROJECT_KEY_1, PROJECT_NAME_1, PROJECT_DESC_1

###############################################################################################

def test_basic_get_projects():
    """
        will return a hash of project keys as keys and project names 
        as values with the getProjects method
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    projects = jp.getProjects()
    assert PROJECT_KEY_1 in projects
    assert projects[PROJECT_KEY_1] == "JEST Testing"

def test_get_project_details():
    """
        will return a array of project details from all projects with get_projects_details
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    details = jp.getProjectsDetails()
    assert details
    tst_details = [entry for entry in details if entry['Key'] == PROJECT_KEY_1]
    assert len(tst_details) > 0
    assert tst_details[0]["Name"] == PROJECT_NAME_1
    assert tst_details[0]["Description"] == PROJECT_DESC_1
    assert tst_details[0]["Details"]["lead"]["name"] == GOOD_VANILLA_SERVER_CONFIG['user']

def test_get_project_uses_cached_info():
    """
        subsequent calls to getProjects returns the cached information
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    projects_initial    = jp.getProjects()
    projects_subsequent = jp.getProjects()

    assert id(projects_initial) == id(projects_subsequent)
    assert PROJECT_KEY_1 in projects_subsequent
    assert projects_subsequent[PROJECT_KEY_1] == "JEST Testing"




