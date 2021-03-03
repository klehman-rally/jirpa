
import sys, os
import py
import re
import copy
import time
from datetime import datetime

from jirpa import JiraProxy, JiraProxyError
from jirpa import JiraFieldSchema
from jirpa import JiraIssueError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG, GOOD_VANILLA_SERVER_DEV_USER_CONFIG 
from jira_targets import PROJECT_KEY_1, PROJECT_NAME_1, PROJECT_KEY_2
from jira_targets import BAD_PROJECT_KEY_1
from jira_targets import JEST_BUG_1

###############################################################################################


def test_update_of_summary_field():
    """
        create a minimal JIRA issue and update the Summary field
    """
    ZLOG = "zooki.log"
    logger = BasicLogger(ZLOG)
    logger.level = 'DEBUG'
    conf = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    conf['logger'] = logger
    jp = JiraProxy(conf)

    #jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "bowling alley decor"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    issue.Summary = "Mr. Bojangles will dance now."
    assert issue.Summary == "Mr. Bojangles will dance now."
    assert jp.updateIssue(issue) == True

    issueAgain = jp.getIssue(issue_key)
    assert issueAgain.Summary == "Mr. Bojangles will dance now."
      
    assert jp.deleteIssue(issue_key)

def test_update_summary_desc_priority_assignee_fields():

    """
        create a minimal JIRA issue and update the Summary, Description, Priority and Assignee fields
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "nothing happnin here..."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    issue.Summary = "Indiana Jones and his hat"
    issue.Description = "wool fedora"
    issue.Priority =  "Highest"
    issue.Assignee =  GOOD_VANILLA_SERVER_DEV_USER_CONFIG['user']
    assert jp.updateIssue(issue) == True

    issueAgain = jp.getIssue(issue_key)

    assert issueAgain.Summary      == "Indiana Jones and his hat"
    assert issueAgain.Description  == "wool fedora"
    assert issueAgain.Priority     == "Highest"
    assert issueAgain.Assignee     == GOOD_VANILLA_SERVER_DEV_USER_CONFIG['user']

    assert jp.deleteIssue(issue_key)

def test_update_rallyid_and_rallyitem_fields():

    """
        create a JiraIssue and update the RallyID and RallyItem fields
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "for custom field updating purposes"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    issue.RallyID     = 45981298
    issue.RallyItem   = "DE8822"
    assert jp.updateIssue(issue) == True

    issueAgain = jp.getIssue(issue_key)

    assert issueAgain.RallyID    == 45981298
    assert issueAgain.RallyItem  == "DE8822"

    assert jp.deleteIssue(issue_key)

def test_sad_refuse_update_with_invalid_priority_value():

    """
        refuse to update a JIRA issue when provided with an invalid priority value
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "fortrado municipal detention center for pronghorns",
                 "Reporter"    :  "testuser",
                 "Assignee"    :  GOOD_VANILLA_SERVER_DEV_USER_CONFIG['user'],
                 "Priority"    :  "Highest",
                 }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    issue.Priority  = "Waffelicious"
    with py.test.raises(JiraIssueError) as excinfo:
        jp.updateIssue(issue)
    actualErrorMessage = excErrorMessage(excinfo)
    assert '"Waffelicious" not an allowed value for the Priority field' in actualErrorMessage

    assert jp.deleteIssue(issue_key)

def test_sad_refuse_update_with_invalid_reporter_value():

    """
        refuse to update a JIRA issue when provided with an invalid reporter value
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "fundamental physical properties preclude the formation is this solid",
                 "Reporter"    :  "testuser",
                 "Assignee"    :  GOOD_VANILLA_SERVER_DEV_USER_CONFIG['user'],
                 "Priority"    :  "Highest",
                 }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    issue = jp.getIssue(issue_key)
    issue.Reporter = "pelicanbeak"
    with py.test.raises(JiraProxyError) as excinfo:
        jp.updateIssue(issue)
    actualErrorMessage = excErrorMessage(excinfo)
    reporter_bad_pattern = re.compile(r'JIRA update errors .*The reporter specified is not a user')
    assert reporter_bad_pattern.search(actualErrorMessage) is not None

    assert jp.deleteIssue(issue_key)

def test_update_the_issue_type_using_display_name():
    """
        allows update of Jira issue type using the display name Issue Type
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "peltonen skis were the rage in the late 80's and early 90's",
                 "Reporter"    :  GOOD_VANILLA_SERVER_CONFIG['user'],
                 "Assignee"    :  GOOD_VANILLA_SERVER_DEV_USER_CONFIG['user'],
                 "Priority"    :  "Highest",
                }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    issue.Summary = "factory of  stuff"
    issue["Issue Type"] = "Story"
    assert jp.updateIssue(issue) == True
    upd_issue = jp.getIssue(issue_key)
    assert upd_issue["Issue Type"] == "Story"

    assert jp.deleteIssue(issue_key)


def test_sad_refuse_update_when_provided_with_bad_issue_type():
    """
        refuse to update a JIRA issue when provided with a bad issue type
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "peltonen skis were the rage in the late 80's and early 90's",
                 "Reporter"    :  GOOD_VANILLA_SERVER_CONFIG['user'],
                 "Assignee"    :  GOOD_VANILLA_SERVER_DEV_USER_CONFIG['user'],
                 "Priority"    :  "Highest",
                }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    issue.Summary = "this should never leave the factory"
    issue["Issue Type"] = "Bugle"
    with py.test.raises(JiraProxyError) as excinfo:
        issue_key = jp.updateIssue(issue)
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Could not find issuetype by id or name' in actualErrorMessage

    assert jp.deleteIssue(issue_key)

def test_update_with_non_default_priority_and_versions_components_fields():
    """
        create a JIRA issue and then update it with non-default priority 
        value along with version and components values
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    work_item = {'Summary'     :  "stuck vontracular relay caused moribundal"
                                  " shudders while accelerative mode shunt activated",
                 'Reporter'    :  GOOD_VANILLA_SERVER_CONFIG['user'],
                 'Assignee'    :  GOOD_VANILLA_SERVER_DEV_USER_CONFIG['user'],
                 'Description' :  "ice blocks whizzed dangerously close to several portholes",
                 #'Priority'    :  "Critical",
                 'Due Date'     :  "2016-02-20",
                 'Environment' :  "Screaming 60's",
                 'Affects Version/s'    :  "cherry",
                 #'Fix Version/s' :  "lemon",
                 #'Fix Version/s' :  "cherry, peach",
                 #'Components'  :  "Routing"  # not required, must be in list of allowedValues,
                 }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    issue["Priority"] = "Highest"
    issue["Affects Version/s"]  = "vanilla,peach"
    jp.updateIssue(issue)

    issue = jp.getIssue(issue_key)
    assert issue.Priority == "Highest"
    assert issue["Affects Version/s"] == ["vanilla", "peach"]

    assert jp.deleteIssue(issue_key)

"""
    #custom_field_names: [ "epic_link"        "Epic Link", 
    #                      "severity"         "Severity", 
    #                      "rally_release"    "Rally Release", 
    #                      "rallyproject"     "RallyProject", 
    #                      "rallystory"       "RallyStory", 
    #                      "rallyurl"         "RallyURL", 
    #                      "rallytestcase"    "RallyTestCase", 
    #                      "rallyitem"        "RallyItem", 
    #                      "rallylink"        "RallyLink", 
    #                      "rallyid"          "RallyID", 
    #                      "rally_creation_date"  "Rally Creation Date", 
    #                      "target_release"       "Target Release"
    #                      ]
"""

def test_update_several_custom_fields():
    """
        create a JIRA issue and update several custom fields
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    work_item = {"Summary"  :  "potash deposit extraction shifting towards foreign suppliers",
                 "Reporter" :  GOOD_VANILLA_SERVER_CONFIG['user'],
                 "Assignee" :  GOOD_VANILLA_SERVER_DEV_USER_CONFIG['user'],
                 "Priority" :  "Lowest",
                 "Severity" :  "Cosmetic",
                 "RallyProject" :  "Burnside Barbers",
                 "RallyID"  :  123453532,
                 "Rally Creation Date" :  "Earth Day"
                }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)

    issue.RallyProject  = "Downtown Dentists"
    issue.RallyID       = 9883990192
    issue["Rally Creation Date"] = "2021-02-13"

    assert jp.updateIssue(issue) == True
    issue = jp.getIssue(issue_key)
    assert issue.RallyProject == "Downtown Dentists"
    assert issue.RallyID      ==  9883990192
    assert issue["Rally Creation Date"] == "2021-02-13"

    assert jp.deleteIssue(issue_key)

def test_sad_refuse_update_an_invalid_field_name():
    """
        create a JIRA issue and refuse to update when field name is invalid
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"   :  "This does not qualify to become a Bug"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    issue.Summary   = "humma humma hummahhhh..."
    issue.Smurfette = "very blue"
    issue.Hyena     = "spotted"

    with py.test.raises(JiraIssueError) as excinfo:
        jp.updateIssue(issue)
    actualErrorMessage = excErrorMessage(excinfo)
    assert r'Unrecognized field |Smurfette|' in actualErrorMessage

    assert jp.deleteIssue(issue_key)

def test_sad_refuse_update_resolution_with_invalid_value():
    """
        create a minimal JIRA issue and refuse to update the Resolution field 
        when field value is invalid
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "Rally Cloudy Day"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    bad_value = "Foobar"
    assert issue.Resolution is None

    issue.Summary    = "Rally Foggy Day"
    issue.Resolution = bad_value

    with py.test.raises(JiraIssueError) as excinfo:
        jp.updateIssue(issue)
    actualErrorMessage = excErrorMessage(excinfo)
    assert f'"{bad_value}" not an allowed value' in actualErrorMessage

    assert jp.deleteIssue(issue_key)

def test_update_resolution_with_valid_value():
    """
        create a JIRA issue and update the Resolution field when Jira is configured to do so
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "Rally Sunny Day"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)

    assert issue.Resolution is None

    issue.Summary    = "Rally Rainy Day"
    issue.Resolution = "Won't Do"
    assert jp.updateIssue(issue) == True

    issueAgain = jp.getIssue(issue_key)
    assert issueAgain.Summary    == "Rally Rainy Day"
    assert issueAgain.Resolution == "Won't Do"

    assert jp.deleteIssue(issue_key)

def test_sad_fail_update_when_resolution_is_invalid_value():
    """
        will fail to  update the issue when Resolution is set to an 
        invalid value (for jira's configuration of allowed Resolution values), 
        but JIRA is configured to allow setting a Resolution
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "Rally Cloudy Day"}
    issue_key = jp.createIssue(PROJECT_KEY_2, "Bug", work_item)
    issue = jp.getIssue(issue_key)

    assert issue.Resolution is None

    issue.Summary    = "Rally Foggy Day"
    issue.Resolution = "No Sun"

    with py.test.raises(JiraIssueError) as excinfo:
        jp.updateIssue(issue)
    actualErrorMessage = excErrorMessage(excinfo)
    assert f'"No Sun" not an allowed value' in actualErrorMessage

    assert jp.deleteIssue(issue_key)

def test_update_original_estimate_field():
    """
        create an issue without originalEstimate and later update it with originalEstimate
    """
    original_estimate  = '2d 4h'
    remaining_estimate = '2d 6h'
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "Another Blustery Day"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue = jp.getIssue(issue_key)
    assert issue['Time Tracking'] == {}
    issue['Time Tracking'] = { 'originalEstimate' :  original_estimate} 
    #   don't try this: 
    #     issue['Time Tracking']['originalEstimate'] = original_estimate 
    #   It will not work and you will be sad and you will gnash your teeth...

    assert jp.updateIssue(issue) == True
    issueAgain = jp.getIssue(issue_key)
    assert issueAgain['Time Tracking']['originalEstimate'] == original_estimate
    assert issueAgain['Time Tracking']['remainingEstimate'] == original_estimate

    # you have to set the whole 'Time Tracking' item so that the originalEstimate is not overwritten
    issue['Time Tracking'] = { 'originalEstimate'  :  original_estimate, 
                               'remainingEstimate' :  remaining_estimate} 
    assert jp.updateIssue(issue) == True

    issueAgain = jp.getIssue(issue_key)
    assert issueAgain['Time Tracking']['originalEstimate']  == original_estimate
    assert issueAgain['Time Tracking']['remainingEstimate'] == remaining_estimate

    assert jp.deleteIssue(issue_key)

def test_update_custom_datetime_field():
    """
        get a bug from a getIssue call and update custom datetime field
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    jira_issue = jp.getIssue(JEST_BUG_1)
    assert jira_issue.key  == "JEST-10012"
    assert jira_issue['Support Review Date'] != None
    current_srd = jira_issue['Support Review Date']
    #now_timestamp needs to be in yy-mm-ddTHH:MM:SS.lll format
    now_timestamp = datetime.now().isoformat(timespec="milliseconds")
    jira_issue['Support Review Date'] = now_timestamp
    #print(f"now_timestamp: {now_timestamp}")
    assert jp.updateIssue(jira_issue) == True

    same_jira_issue = jp.getIssue(JEST_BUG_1)
    assert same_jira_issue['Support Review Date'] != None
    assert same_jira_issue['Support Review Date'] != current_srd
    # since we don't know when this particular test was last run we can't really
    # get really specific on comparing what was the 'Support Review Date' then
    # vs what we just set it to



