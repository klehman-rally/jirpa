
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

LOG_FILE_NAME   = "basaltic.log"

###############################################################################################

def test_retrieving_jira_server_info():
    """
        will return a JiraServerInfo
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    assert jp is not None
    assert jp.jira_version is not None
    info = jp.getServerInfo()
    assert info.url == GOOD_VANILLA_SERVER_CONFIG['url']
    assert re.search(r'^7\.([2-9])', info.version) is not None


def test_retrieving_jira_users():
    """
        will return a set of JiraUser instances
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    users = jp.getUsers(PROJECT_KEY_1)
    assert len(users) > 0
    hits = [u for u in users if u.name == USER1_USER_NAME]
    assert len(hits) == 1
    target_user = hits[0]
    assert target_user.name   == USER1_USER_NAME
    assert target_user.email  == USER1_EMAIL
    assert target_user.active == USER1_ACTIVE


def test_retrieve_jira_schema_for_field():
    """
        will return a JiraFieldSchema instance for a valid field
    """
    SLOG = "getschema.log"
    logger = BasicLogger(SLOG)
    logger.level = 'DEBUG'
    conf = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    conf['logger'] = logger

    jp = JiraProxy(conf)
    fs = jp.fieldSchema(PROJECT_KEY_1, 'Bug', 'Priority')
    assert fs.__class__  == JiraFieldSchema
    assert fs.display_name == 'Priority'
    assert fs.standard   == True
    assert fs.custom     == False
    assert fs.structure  == 'atom'
    assert fs.data_type  == 'priority'
    assert 'High' in fs.allowed_values

    log_lines = []
    with open(SLOG, 'r') as lf:
        log_lines = lf.readlines()
    log_debug_line_with_field_info_patt \
        = re.compile(r':DEBUG:.*:JiraProxy config arg content:.*password.*')
    re.compile(r":DEBUG:.*:.*field_info returned from JIRA options-[^\n]+ were:\n")
    lines_with_field_info = [line for line in log_lines 
                             if log_debug_line_with_field_info_patt.search(line)]
    assert len(lines_with_field_info) == 1

    os.remove(SLOG)


def test_get_jira_schema_for_valid_project():
    """
        return a JiraFieldSchema instance for a valid field using a valid project name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    fs = jp.fieldSchema(PROJECT_NAME_1, 'Bug', 'Priority')

    assert fs.__class__    == JiraFieldSchema
    assert fs.display_name ==  'Priority'
    assert fs.standard     == True
    assert fs.custom       == False
    assert fs.structure    == 'atom'
    assert fs.data_type    == 'priority'
    assert 'Low' in fs.allowed_values


def test_sad_get_jira_schema_for_invalid_project():
    """
        will raise an error on attempt to return a JiraFieldSchema instance 
        for a valid field for an invalid project identifier
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    with py.test.raises(JiraProxyError) as excinfo:
        fs = jp.fieldSchema(BAD_PROJECT_KEY_1, 'Bug', 'Priority')
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Could not find project for identifier:' in actualErrorMessage


def test_get_jira_schema_for_array_valued_field():
    """
        will return a JiraFieldSchema instance for a valid field that is an array
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    fs = jp.fieldSchema(PROJECT_KEY_1, 'Bug', 'Affects Version/s')

    assert fs.__class__    == JiraFieldSchema
    assert fs.display_name == 'Affects Version/s'
    assert fs.standard     == True
    assert fs.custom       == False
    # FIX!
    #assert fs.structure    == 'array'   # this fails, it comes back as 'atom'
    assert fs.data_type    == 'array'
    assert 'vanilla' in fs.allowed_values


def test_get_jira_schema_for_custom_string_field():
    """
        will return a JiraFieldScheme instance for a valid custom field of type string
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    fs = jp.fieldSchema(PROJECT_KEY_1, 'Bug', 'RallyURL')

    assert fs.__class__    == JiraFieldSchema
    assert fs.display_name == 'RallyURL'
    assert fs.standard     == False
    assert fs.custom       == True
    assert fs.name.startswith('customfield_')
    assert fs.structure    == 'atom'
    assert fs.data_type    == 'string'
    assert not fs.allowed_values


def test_get_jira_schema_for_custom_number_field():
    """
        will return a JiraFieldScheme instance for a valid custom field of type number
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    fs = jp.fieldSchema(PROJECT_KEY_1, 'Bug', 'RallyID')

    assert fs.__class__    == JiraFieldSchema
    assert fs.display_name == 'RallyID'
    assert fs.name.startswith('customfield_')
    assert fs.standard     == False
    assert fs.custom       == True
    assert fs.structure    == 'atom'
    assert fs.data_type    == 'number'
    assert not fs.allowed_values


