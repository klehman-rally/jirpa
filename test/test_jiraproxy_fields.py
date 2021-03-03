
import sys, os
import py
import re

from jirpa import JiraProxy, JiraProxyError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG, GOOD_VANILLA_SERVER_DEV_USER_CONFIG 
from jira_targets import GOOD_VANILLA_ONDEMAND_REGULAR_USER_CONFIG
from jira_targets import PROJECT_KEY_1, PROJECT_NAME_1, PROJECT_DESC_1
from jira_targets import BAD_PROJECT_KEY_1


LOG_FILE_NAME   = "anthracite.log"

###############################################################################################

def test_identify_standard_known_field():
    """
        correctly identify that a known standard field exists
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    sfs = jp.getStandardFields(PROJECT_KEY_1, 'Bug')
    assert "Description" in sfs
    assert jp.fieldExists(PROJECT_KEY_1, "Bug", "Summary")

    assert jp.fieldExists(PROJECT_KEY_1, "Story", "Summary")
    assert jp.fieldExists(PROJECT_KEY_1, "Story", "Status")


def test_bug_field_retrieval():
    """
        check that the Description, Summary and Status fields can be retrieved for a Bug
    """
    jp = JiraProxy(GOOD_VANILLA_ONDEMAND_REGULAR_USER_CONFIG)
    #sfs = jp.getStandardFields(PROJECT_KEY_1, 'Story')
    sfs = jp.getStandardFields(PROJECT_KEY_1, 'Bug')
    assert "Description" in sfs
    assert jp.fieldExists(PROJECT_KEY_1, "Bug", "Summary")
    assert jp.fieldExists(PROJECT_KEY_1, "Bug", "Status")


def test_standard_bug_field_presence():
    """
        should correctly identify that a known standard field exists using a valid project name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    sfs = jp.getStandardFields(PROJECT_NAME_1, 'Bug')
    assert "Description" in sfs
    assert jp.fieldExists(PROJECT_NAME_1, "Bug", "Summary")


def test_sad_bad_project_specfied():
    """
        raise an error on attempt to identify that a known standard field 
        exists using an invalid project identifier
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    sfs = jp.getStandardFields(PROJECT_KEY_1, 'Bug')
    assert "Description" in sfs
    with py.test.raises(Exception) as excinfo:
        jp.fieldExists(BAD_PROJECT_KEY_1, "Bug", "Summary")
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Could not find project for identifier:' in actualErrorMessage

"""   Antecedent system originating this test had an older Jira 6 system with a user not having rights
      This test is probably overkill and not necessary.
"""
def hide_test_sad_no_such_issue_type_for_project():
    """
        could not find issue type bug in project jest
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    with py.test.raises(JiraProxyError) as excinfo:
        jp.getStandardFields(PROJECT_KEY_1, 'Bug') 
    actualErrorMessage = excErrorMessage(excinfo)
    assert ': Could not find Issue Type "Bug" in Project "JEST".' in actualErrorMessage
    assert 'Ensure the Issue Type "Bug" is available ' in actualErrorMessage


def test_non_writable_data_fields():
    """
        recognize standard non-writable date fields
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    sfs = jp.getStandardFields(PROJECT_KEY_1, 'Bug')
    assert jp.fieldExists(PROJECT_KEY_1, 'Bug', 'created')
    assert jp.fieldExists(PROJECT_KEY_1, 'Bug', 'CreatedDate')
    assert jp.fieldExists(PROJECT_KEY_1, 'Bug', 'createddate')
    assert jp.fieldExists(PROJECT_KEY_1, 'Bug', 'Created Date')

    assert jp.fieldExists(PROJECT_KEY_1, 'Bug', 'updated')
    assert jp.fieldExists(PROJECT_KEY_1, 'Bug', 'UpdatedDate')
    assert jp.fieldExists(PROJECT_KEY_1, 'Bug', 'updateddate')
    assert jp.fieldExists(PROJECT_KEY_1, 'Bug', 'Updated Date')


def test_for_known_custom_field():
    """
        correctly identify that a known custom field exists
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    cfs = jp.getCustomFields(PROJECT_KEY_1, 'Bug')
    assert "RallyItem" in cfs
    assert jp.fieldExists(PROJECT_KEY_1, "Bug", "RallyID")

    jp2 = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    assert jp2.isCustomField(PROJECT_KEY_1, "Bug", "RallyURL")


def test_valid_project_has_custom_fields():
    """
        should correctly identify that a known custom field exists for a valid project name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    cfs = jp.getCustomFields(PROJECT_NAME_1, 'Bug')
    assert "RallyItem" in cfs
    assert jp.fieldExists(PROJECT_NAME_1, "Bug", "RallyID")

    jp2 = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    assert jp2.isCustomField(PROJECT_NAME_1, "Bug", "RallyURL")


def test_sad_bad_project_prevents_seeing_custom_field():
    """
        raises an error on attempt to identify that a known custom field 
        exists with an invalid project identifier
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    cfs = jp.getCustomFields(PROJECT_KEY_1, 'Bug')
    assert "RallyItem" in cfs
    assert jp.fieldExists(PROJECT_KEY_1, "Bug", "RallyID")
    with py.test.raises(JiraProxyError) as excinfo:
        trvth  = jp.isCustomField(BAD_PROJECT_KEY_1, "Bug", "RallyURL")
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Could not find project for identifier:' in actualErrorMessage


def test_detect_bogus_field_does_not_exist():
    """
        detects that a Bogus field does not exist
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    assert jp.fieldExists(PROJECT_KEY_1, "Bug", 'Bogus') == False


def test_fields_with_multiple_word_display_name():
    """
        list all fields whose display name is a multiple word string
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    sfs = jp.getStandardFields(PROJECT_KEY_1, 'Bug')
    cfs = jp.getCustomFields(PROJECT_KEY_1, 'Bug')

    standard_multi_word_fields = [fn for fn in sfs if fn.count(' ') > 0]
    custom_multi_word_fields   = [fn for fn in cfs if fn.count(' ') > 0]
    assert len(standard_multi_word_fields) > 0
    assert len(custom_multi_word_fields)   > 0

    multi_word_bug_fields = """Advent Category,
        Affects Version/s,
        Due Date,
        Issue Type,
        Rally Creation Date,
        RallyID,
        RallyItem,
        Story Points,
        Target Release,
        Time Tracking
       """.split(',')

    assert 'Rally Creation Date' in custom_multi_word_fields


