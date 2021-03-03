
import sys, os
import py
import re
import copy
from datetime import datetime

from jirpa import JiraProxy, JiraProxyError

###############################################################################################

from helper_pak   import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG, GOOD_VANILLA_ONDEMAND_CONFIG
from jira_targets import INCOMPLETE_CONFIG 
from jira_targets import PROJECT_KEY_1, PROJECT_NAME_1, PROJECT_DESC_1
from jira_targets import BAD_PROJECT_KEY_1
from jira_targets import GOOD_ONDEMAND_VIA_GOOD_PROXY_CONFIG
from jira_targets import SUSPECT_ONDEMAND_VIA_NONEXISTENT_PROXY_CONFIG
from jira_targets import SUSPECT_ONDEMAND_VIA_BAD_PROXY_CONFIG

DEFAULT_TIMEOUT = 30
BAD_SERVER_VERBIAGE = r'Failed to establish a new connection: .* ' + \
                      r'nodename nor servname provided, or not known'
LOG_FILE_NAME   = "granitic.log"

###############################################################################################

def test_obtaining_jira_proxy_instance():

    """
        will create with new using URL, user, password and project
    """
    with py.test.raises(JiraProxyError) as excinfo:
        jp = JiraProxy(INCOMPLETE_CONFIG)
    actual_error_message = excErrorMessage(excinfo)
    assert actual_error_message == 'JiraProxy requires the config item for password to be present'

    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    assert jp is not None


def test_using_logger_in_jira_proxy():
    """
        should support a logger option when instantiating a JiraProxy instance
    """
    ##TODO Fix logger test so that it passes in Jenkins
    
    logger = BasicLogger(LOG_FILE_NAME)
    logger.level = 'DEBUG'
    conf = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    conf['logger'] = logger
    jp = JiraProxy(conf)
    assert jp is not None
    assert os.path.exists(LOG_FILE_NAME)
    os.remove(LOG_FILE_NAME)


def test_get_issue_type_info():
    """
        will return issue types with issue_types and issue_type_map
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    issue_types,issue_type_map = jp.getIssueTypes()

    assert "Bug"   in issue_types
    assert "Story" in issue_types

    ## TODO Should we really be testing the id values for issue_type_map ?
    assert issue_type_map["Story"]["id"] == "10001"
    assert issue_type_map["Bug"]["id"]   == "10006"

def test_get_status_info():
    """
        will return status values and id's
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
 
    status_values = jp.getStatuses()
    # In JIRA 7.x, the default workflow Story status list is:
    #   ['In Progress', 'To Do', 'In Review', 'Done']
    #   with no proscribed state change restrictions
 
    assert "To Do"       in status_values
    assert "In Progress" in status_values
 
    ## TODO Should we really be testing the it values for status_values ?
    assert jp.status_value_for_id["10000"] == "To Do"
    assert jp.status_value_for_id["3"]     == "In Progress"
    inverted_status_value_for_id \
            = {value:key for key,value in jp.status_value_for_id.items()}
    assert inverted_status_value_for_id["In Progress"] == "3"

def test_get_priority_info():
    """
        will return priority value and id's
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    priority_values = jp.getPriorities()

    assert "High"    in priority_values
    assert "Highest" in priority_values
    assert "Medium"  in priority_values
    assert "Low"     in priority_values
    assert "Lowest"  in priority_values

    ## TODO Should we really be testing the id values ?
    assert jp.priority_value_for_id["3"] == "Medium"
    assert jp.priority_value_for_id["2"] == "High"
    inverted_priority_value_for_id \
            = {value:key for key,value in jp.priority_value_for_id.items()}
    assert inverted_priority_value_for_id["High"] == "2"

def test_get_resolution_info():
    """
        will return resolution value and id's
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    resolution_values = jp.getResolutions()

    assert "Done"     in resolution_values
    assert "Won't Do" in resolution_values

    ## TODO Test ID values ?
    assert jp.resolution_value_for_id["10000"] == "Done"
    assert jp.resolution_value_for_id["10001"] == "Won't Do"

    inverted_resolution_value_for_id \
            = {value:key for key,value in jp.resolution_value_for_id.items()}
    assert inverted_resolution_value_for_id["Won't Do"] == "10001"

def test_get_standard_fields_list_for_project_key():
    """
        will return an array of standard field names for an issue type related to a project key
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    standard_field_names = jp.getStandardFields(PROJECT_KEY_1, "Bug")
    assert "Reporter" in standard_field_names
    assert "Assignee" in standard_field_names

def test_get_standard_fields_list_for_project_name():
    """
        returns an array of standard field names
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    standard_field_names = jp.getStandardFields(PROJECT_NAME_1, "Bug")
    assert "Summary" in standard_field_names
    assert "Reporter" in standard_field_names
    assert "Priority" in standard_field_names
    assert "Affects Version/s" in standard_field_names

def test_using_invalid_project_raises_error():
    """
        on attempt to get standard field names using an invalid project will raise an error
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    with py.test.raises(JiraProxyError) as excinfo:
        standard_field_names = jp.getStandardFields(BAD_PROJECT_KEY_1, "Bug")
    actualErrorMessage = excErrorMessage(excinfo)
    assert actualErrorMessage == f'Could not find project for identifier: {BAD_PROJECT_KEY_1}'

def test_get_custom_field_names_list():
    """
        will return an array of custom field names
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    custom_field_names = jp.getCustomFields(PROJECT_KEY_1, "Story")
    assert "RallyID" in custom_field_names

def test_get_custom_field_names_for_project():
    """
        returns an array of custom field names for a valid project name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    custom_field_names = jp.getCustomFields(PROJECT_NAME_1, "Story")
    assert "RallyID" in custom_field_names

def test_bad_proj_ident_raises_error():
    """
        attempt to get custom fields using a bad project identifier will raise an error
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    with py.test.raises(JiraProxyError) as excinfo:
        custom_field_names = jp.getCustomFields(BAD_PROJECT_KEY_1, "Story")
    actualErrorMessage = excErrorMessage(excinfo)
    assert actualErrorMessage == f'Could not find project for identifier: {BAD_PROJECT_KEY_1}'

def test_show_all_groups_for_user():
    """
        will return an array of groups that a user belongs to
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    groups = jp.getGroups(GOOD_VANILLA_SERVER_CONFIG['user'])
    assert "monsieur-connecteur" in groups
    assert "jira-software-users" in groups

    # deselected by virtue of hide prefix for now, 
    #  but this has to be proven that it can work with an HTTP/HTTPS proxy server
    #   attempting connect through a non-existent https proxy will raise an exception
def hide__test_obtain_jira_issue_types_through_proxy():
    """
        Through a proxy, will return issue types with issue_types and issue_type_map
    """
    # first deal with the 'InsecureRequestWarning: Unverified HTTPS request ....' issue whilst testing
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    jp = JiraProxy(GOOD_ONDEMAND_VIA_GOOD_PROXY_CONFIG)

    issue_types,issue_type_map = jp.getIssueTypes()
    assert "Bug"   in issue_types
    assert "Story" in issue_types

    # Specifying an invalid proxy host, will raise an exception
    import requests
    with py.test.raises(requests.exceptions.ProxyError) as excinfo:
        jp = JiraProxy(SUSPECT_ONDEMAND_VIA_NONEXISTENT_PROXY_CONFIG)
    actualErrorMessage = excErrorMessage(excinfo)
    assert "Failed to establish a new connection" in actualErrorMessage
    assert "nodename nor servname provided, or not known" in actualErrorMessage

    # Through a invalid proxy user, will raise an exception
    with py.test.raises(JiraProxyError) as excinfo:
        jp = JiraProxy(SUSPECT_ONDEMAND_VIA_BAD_PROXY_CONFIG)
    actualErrorMessage = excErrorMessage(excinfo)
    print('-----')
    print(actualErrorMessage)

def test_show_password_as_fuzzed():
    """
        will show password as ***** in debug statements
    """
    TLOG = "transitory.log"
    logger = BasicLogger(TLOG)
    logger.level = 'DEBUG'
    conf = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    conf['logger'] = logger
    jp = JiraProxy(conf)
    log_lines = []
    with open(TLOG, 'r') as lf:
        log_lines = lf.readlines()
    log_debug_line_with_config_info_patt \
        = re.compile(r':DEBUG:.*:JiraProxy config arg content:.*password.*')
    lines_with_password = [line for line in log_lines 
                                 if re.search(log_debug_line_with_config_info_patt, line)]
    assert len(lines_with_password) == 1
    assert '*****' in lines_with_password[0]

    os.remove(TLOG)

