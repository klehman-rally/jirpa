
import sys, os
import py, pytest
import re
import copy
from datetime import datetime

from jirpa import JiraProxy, JiraProxyError
from jirpa import JiraFieldSchema
from jirpa import JiraIssueError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG, GOOD_VANILLA_SERVER_DEV_USER_CONFIG 
from jira_targets import PROJECT_KEY_1, PROJECT_NAME_1
from jira_targets import BAD_PROJECT_KEY_1

###############################################################################################

#def deleteIssue(target):
#    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
#    jp.deleteIssue(target) or print(f"{target.key} not deleted")
#end
#
#@pytest.fixture(autouse=True)
#def run_before_and_after_tests():
#    """
#        Fixture to execute asserts before and after a test is run
#    """
#    # Setup: fill with any logic you want  aka before each
#    print("\nin to the pool")
#
#    yield # this is where the testing happens
#
#    # Teardown : fill with any logic you want  # aka after each
#    print("\nout of the pool...")
    
###############################################################################################

def test_minimal_create():
    """
        create a minimal JIRA issue via the createIssue method
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" : "kindergarten hopscotch games"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')

    assert issue_key_patt.match(issue_key)
    assert jp.deleteIssue(issue_key)


def test_minimal_create_with_valid_project():
    """
        should create a minimal JIRA issue via the createIssue method when given valid project name
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "kindergarten hopscotch games"}
    issue_key = jp.createIssue(PROJECT_NAME_1, "Bug", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')

    assert issue_key_patt.match(issue_key)
    assert jp.deleteIssue(issue_key)

def test_sad_issue_create_with_invalid_project():
    """
        raises an error on attempt to create a minimal JIRA issue via 
        the createIssue method using an invalid project identifier
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "kindergarten hopscotch games"}
    with py.test.raises(JiraProxyError) as excinfo:
        issue_key = jp.createIssue(BAD_PROJECT_KEY_1, "Bug", work_item)
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Could not find project for identifier:' in actualErrorMessage

def test_issue_create_populates_attributes():
    """
        exercise the ability of the JiraIssue to supply attribute information
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "nothing happnin here..."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)
    issue = jp.getIssue(issue_key)
    assert issue
    eam = issue.attributeDisplayNames()
    assert len(eam) > 20 

    av = issue.attributeValues()
    assert len(av) > 32 

    assert jp.deleteIssue(issue_key)

def test_issue_create_with_many_standard_fields():
    """
        create a JIRA issue with many of the standard fields populated
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "elementary gym class dodge ball tournament",
                 "Reporter"    :  "testuser",
                 "Assignee"    :  "devuser",
                 "Description" :  "Blend 4 parts of enthusiasm with 3 parts coordination " +\
                                  "and 1 part courage.  Shake well. Dodge Ball!",
                 "Due Date"    :  "2021-02-17",
                 "Environment" :  "Sultry Hot!",
                 }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    assert jp.deleteIssue(issue_key)

def test_datetime_field_value_is_jira_compliant():
    """
        the data for a JIRA datetime field should be in JIRA compliant format
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "Egotistical Felon",
                 "Reporter"    :  "testuser",
                 "Assignee"    :  "devuser",
                 "Description" :  "Those pesky reds have harpooned me again!",
                "Support Review Date"    :  "2021-03-10T05:23:00.000Z"
                }

    jira_item = {"key" :  "JEST-0000",  "fields"  :  work_item  }
    jira_item["fields"]["issuetype"] = {"name" :  'Bug'}
    issue = jp.makeAnIssueInstance(jira_item)
    postable_issue_data = issue.jiralize('create')

    JIRA_INBOUND_DATETIME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.000-0000$')

    assert JIRA_INBOUND_DATETIME_PATTERN.match(postable_issue_data['fields']['customfield_10200'])


def test_create_issue_with_datetime_field_value():
    """
        create a JIRA Bug with a timedate field
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "Fazeko Bituminousm",
                 "Reporter"    :  "testuser",
                 "Assignee"    :  "devuser",
                 "Description" :  "hard boiled bacon bobs slake all appetites",
                 "Support Review Date"    :  "2020-02-17T18:45:00"  # gets converted to Jira compliant
                }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    assert jp.deleteIssue(issue_key)

def test_sad_bypass_create_when_bad_issue_type():
    """
        Refuse to create a JIRA issue when issue type is invalid
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "elementary gym class dodge ball tournament",
                 "Reporter"    :  "testuser",
                 "Assignee"    :  "devuser",
                 "Description" :  "Blend 4 parts of enthusiasm with 3 parts coordination and 1 part courage.  Shake well. Dodge Ball!",
                 "Due Date"     :  "2021-02-17",
                 "Environment" :  "Sultry Hot!",
                }
    with py.test.raises(JiraProxyError) as excinfo:
        issue_key = jp.createIssue(PROJECT_KEY_1, "bug", work_item)
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'bad issue type' in actualErrorMessage


def test_sad_bypass_create_when_invalid_priority_value():
    """
        Refuse to create a JIRA issue when provided with an invalid priority value
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "elementary gym class dodge ball tournament",
                 "Reporter"    :  "testuser",
                 "Assignee"    :  "devuser",
                 "Priority"    :  "Waffelicious"
                 }
    with py.test.raises(JiraIssueError) as excinfo:
        issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    actualErrorMessage = excErrorMessage(excinfo)
    assert '"Waffelicious" not an allowed value' in actualErrorMessage

def test_create_issue_with_good_priority_value():
    """
        create a JIRA issue with a validly set Priority field
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "Charlemagne must have his hair styled before the great battle",
                 "Reporter"    :  "testuser",
                 #"Priority"    :  "Critical", # in Jira6
                 "Priority"    :  "High",
                  }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    assert jp.deleteIssue(issue_key)

def test_create_issue_using_display_name_for_fields():
    """
        Test uses Display name.
           create a JIRA issue from a work item having keys matching the case in JIRA display
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"     :  "Wontons and flipped rice noodles make a " 
                                  "carbo-loaded snack rich with flavor",
                 "Reporter"    :  "testuser",
                 "Assignee"    :  "devuser",
                 "Priority"    :  "Low",
                 "Description" :  "rumplestilskin venture capitalist mediocre pomogranatic oxidants",
                 "Due Date"    :  "2020-04-22"
                }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    assert jp.deleteIssue(issue_key)

def test_create_issue_using_system_names_for_fields():
    """
        create a JIRA issue from a work item having symbol keys associated with standard fields
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    
    work_item = {'summary'     :  "kids again forgot to put away superhero capes and masks properly",
                 'reporter'    :  "testuser",
                 'assignee'    :  "devuser",
                 'description' :  "Several vents were blocked and noxious gases spilled into the parlor",
                 'duedate'     :  "2021-02-18",
                 'environment' :  "Howling",
                 }
    
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    assert jp.deleteIssue(issue_key)

def test_create_issue_with_non_default_priority_and_version_and_component_values():
    """
        create a JIRA issue with non-default priority value along with version and components values
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    work_item = {'Summary'       :  "stuck vontracular relay caused moribundal shudders " + \
                                    "while accelerative mode shunt activated",
                 'Reporter'      :  "testuser",
                 'Assignee'      :  "devuser",
                 'Description'   :  "ice blocks whizzed dangerously close to several portholes",
                #"Priority"      :  "Critical", # in Jira6
                 "Priority"      :  "High",
                 'Due Date'      :  "2020-09-20",
                 'Environment'   :  "Screaming 60's",
                 'Affects Version/s' :  "vanilla",
                #'fixversions'   :  "lemon", 
                 'Fix Version/s' :  "cherry, peach",
                 'Component/s'   :  "Routing"  # not required, must be in list of allowedValues,
                 }

    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    assert jp.deleteIssue(issue_key)


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

def test_create_issue_with_several_custom_fields():
    """
        create a JIRA issue with several custom fields set
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    work_item = {"Summary"   :  "potash deposit extraction shifting towards foreign suppliers",
                 "Reporter"  :  "testuser",
                 "Assignee"  :  "devuser",
                 "Priority"  :  "Lowest",
                 "Severity"  :  "Cosmetic",
                 "RallyID"   :  123453532,
                 "RallyProject" :  "Burnside Barbers",
                 "Rally Creation Date" :  "Earth Day"
                }

    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    assert jp.deleteIssue(issue_key)

def test_create_issue_with_attempt_to_set_non_initial_status():
    """
        create a JIRA issue with an attempt to set a non-initial status,
        but created issue should have the prescribed initial status
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    work_item = {"Summary"  :  "lost in 3 trees",
                 "Reporter" :  "testuser",
                 "Assignee" :  "devuser",
                 "Status"   :  "In Progress"
                }

    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    full_issue = jp.getIssue(issue_key)

    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)
    assert full_issue.status != "In Progress"

    assert jp.deleteIssue(issue_key)

def test_sad_refuse_to_create_when_reporter_value_is_bad():
    """
        refuse to create a JIRA issue when the reporter value is invalid
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"  :  "Don't even think of creating me",
                 "Reporter" :  "jamesbond"
                }
    with py.test.raises(JiraProxyError) as excinfo:
        issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    actualErrorMessage = excErrorMessage(excinfo)
    create_issue_error_pattern = re.compile(r'Creating issue.*failed.*reporter')
    assert create_issue_error_pattern.search(actualErrorMessage) is not None

def test_sad_refuse_to_create_when_assignee_value_is_bad():
    """
        refuse to create a JIRA issue when the assignee value is invalid
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"  :  "This does not qualify to become a Bug",
                 "Assignee" :  "bobmarley"
                }
    with py.test.raises(JiraProxyError) as excinfo: 
        issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    actualErrorMessage = excErrorMessage(excinfo)
    create_issue_error_pattern = re.compile(r'Creating issue.*failed.*assignee')
    assert create_issue_error_pattern.search(actualErrorMessage) is not None

def test_sad_refuse_to_create_when_both_reporter_and_assignee_values_are_bad():
    """
        refuse to create a JIRA issue when the assignee and reporter values are invalid
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"  :  "This does not qualify to become a Bug",
                 "Reporter" :  "halestorm",
                 "Assignee" :  "hayleywilliams"
                }
    with py.test.raises(JiraProxyError) as excinfo:
        issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    actualErrorMessage = excErrorMessage(excinfo)
    create_issue_error_pattern = re.compile(r'Creating issue.*failed.*reporter.*assignee')
    assert create_issue_error_pattern.search(actualErrorMessage) is not None


def test_sad_refuse_to_create_when_bad_field_name_is_specified():
    """
        refuse to create a JIRA issue when field name is invalid
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary"   :  "This does not qualify to become a Bug",
                 "Smurfette" :  "very blue",
                 "MentalAnguish" : "bordering on insanity!"
                 }
    with py.test.raises(JiraIssueError) as excinfo:
        issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    actualErrorMessage = excErrorMessage(excinfo)
    create_issue_error_pattern = re.compile(r'Unrecognized field.*Smurfette')
    assert create_issue_error_pattern.search(actualErrorMessage) is not None

def test_sad_refuse_create_when_attempt_to_supply_comment():
    """
        should not be able to create a Comment at issue creation
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)

    work_item = {"Summary" :  "bowling alley decor",
                 "Comment" :  "Green Bowling balls suck."}
    with py.test.raises(JiraIssueError) as excinfo:
        jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    actualErrorMessage = excErrorMessage(excinfo)
    assert r'Unrecognized field |Comment|' in actualErrorMessage

def test_create_a_new_feature_issue_type():
    """
        create a JIRA New Feature issue via the createIssue method
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = { "Summary" :  "Chattanooga ChooChooz",
                  "Status"  :  "Open",
                  "RallyID" :  "10921026054",
                  "RallyItem" :  "S7302",
                  "RallyURL" :  "https://trial.rallydev.com/slm/#/detail/userstory/10921026054"
                }
    issue_key = jp.createIssue(PROJECT_KEY_1, "New Feature", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)
    new_feature = jp.getIssue(issue_key)
    assert new_feature['key'] == issue_key
    #for field_name in new_feature.attributes() do
    #   print("  %18.18s  =  %s" % (field_name, new_feature[field_name]])
    #end

    assert jp.deleteIssue(issue_key)

def test_create_story_with_single_custom_multiselect_field():
    """
        create a JIRA New Story issue that sets a multiselect custom field
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = { "Summary"         :  'Veg Stand',
                  "Advent Category" :  'green beans'}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Story", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)
    story_issue = jp.getIssue(issue_key)

    assert story_issue['Advent Category'] == ['green beans']

    assert jp.deleteIssue(issue_key)

def test_create_story_with_two_custom_multiselect_fields():
    """
        create a JIRA New Story issue that sets two multiselect custom field
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = { "Summary" :  'Green Veg Stand',
                  "Advent Category" :  'green beans, spinach'}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Story", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    story_issue = jp.getIssue(issue_key)
    assert story_issue['Advent Category'].__class__ == list
    assert 'green beans' in story_issue['Advent Category']
    assert 'spinach'     in story_issue['Advent Category']

    assert jp.deleteIssue(issue_key)

def test_create_story_setting_one_value_for_label():
    """
        create a JIRA New Story issue that sets one label standard field
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = { "Summary" :  'Labels of one state',
                  "Labels"  :  'Confusion' }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Story", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    story_issue = jp.getIssue(issue_key)
    assert story_issue['Labels'] == "Confusion"

    assert jp.deleteIssue(issue_key)

def test_create_story_setting_two_values_for_labels():
    """
        create a JIRA New Story issue that sets two labels standard field
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = { "Summary" :  'Labels of two states',
                  "Labels"  :  'Virginia,Colorado' }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Story", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    story_issue = jp.getIssue(issue_key)
    assert story_issue['Labels'].__class__ == str
    assert 'Virginia' in story_issue['Labels']
    assert 'Colorado' in story_issue['Labels']

    assert jp.deleteIssue(issue_key)

def test_create_story_with_original_estimate_field_set():
    """
        create a new JIRA Story with the OriginalEstimate field value set
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = { "Summary" :  'Units of hard labor required to spring ex-presidential candidates from prison',
                #  "timetracking" :  {'originalEstimate' :  '4m 2w 3d'} }
                 "timetracking" :  {'originalEstimate' :  '6w 2d 4h'} }
    issue_key = jp.createIssue(PROJECT_KEY_1, "Story", work_item)
    issue_key_patt = re.compile(f'^{PROJECT_KEY_1}-\\d+')
    assert issue_key_patt.match(issue_key)

    story_issue = jp.getIssue(issue_key)
    #print( story_issue.attributes )
    #print( "Issue: #{issue_key}  Summary: #{story_issue['Summary']}" )
    #print( "timeestimate: #{story_issue.timeestimate}" )
    #print( "timeoriginalestimate: #{story_issue.timeoriginalestimate}" )
    #print( "---------------------------------------------" )
    #print( "Time Tracking: #{story_issue['Time Tracking']}" )
    #print( "---------------------------------------------" )
    #print( "Time Tracking: -> originalEstimate #{story_issue['Time Tracking']['originalEstimate']}" )
    assert story_issue['Time Tracking']['originalEstimate'] == "6w 2d 4h"

    assert jp.deleteIssue(issue_key)


