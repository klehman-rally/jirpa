
import sys, os
import py

from jirpa import JiraProxy, JiraProxyError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG, GOOD_VANILLA_SERVER_DEV_USER_CONFIG 
from jira_targets import CONFIG_3
from jira_targets import PROJECT_KEY_1, PROJECT_NAME_1, PROJECT_KEY_2
from jira_targets import PROJECT_KEY_3, PROJECT_KEY_4

###############################################################################################

#   JiraProxy state transitions and operations

    # to use with Rally workflow  ( a more restrictive workflow than the Simplified Workflow provided by JIRA 7)
    # So, we imported from Jira 6 a more restrictive workflow called 'Rally Workflow' (that we created back in 2012/2013)
    # and the following scenario passes in Jira 7.  We created a new Project (named in PROJECT_KEY_4) and associated
    # the workflow with that project.
    # We also noted that
    #  1) jp.transitionIssueState(issue_key, status) works when the 3rd argument, resolution, defaults to nil works as long as Resolution is added to Bug Screen
    #  2) jp.transitionIssueState(issue_key, status, resolution) fails when Simplified Workflow provided by JIRA 7 is associated with the project
    #  3) jp.transitionIssueState(issue_key, status, resolution) works when a more restrictive workflow (like the RallyWorkflow) is associated with the project

def test_transition_bug_to_resolved_state():
    """
        transition a bug in RW project to Resolved
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" : "Roller Coaster assembly point"}
    issue_key = jp.createIssue(PROJECT_KEY_4, "Bug", work_item)

    jp.transitionIssueState(issue_key, "Resolve Issue", "Won't Fix" )
    issue = jp.getIssue(issue_key)
    assert issue.Status == "Resolved"
    assert issue.Resolution == "Won't Fix"
    assert jp.deleteIssue(issue_key)

def test_list_transitions_for_newly_created_issue_by_admin_user():
    """
        list transitions that an newly created issue can use 
        with getTransitions as a admin user
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" : "Disneyland is great."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    transitions = jp.getTransitions(issue_key)
    # If the PROJECT_KEY_4 is used the following lines would work
    #assert "Start Progress"  in transitions.keys()
    #assert "Resolve Issue"   in transitions.keys()
    #assert "Close Issue"     in transitions.keys()
    assert "To Do"       in transitions.keys()
    assert "In Progress" in transitions.keys()
    assert "In Review"   in transitions.keys()
    assert "Done"        in transitions.keys()
    assert jp.deleteIssue(issue_key)

def test_list_transitions_for_newly_created_issue_by_dev_user():
    """
        list transitions that an newly created issue can use 
        with getTransitions as a dev user
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Six flags is good too."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    transitions = jp.getTransitions(issue_key)
    # If the PROJECT_KEY_4 is used the following lines would work
    #assert "Start Progress"  in transitions.keys()
    #assert "Resolve Issue"   in transitions.keys()
    #assert "Close Issue"     in transitions.keys()
    assert "To Do"       in transitions.keys()
    assert "In Progress" in transitions.keys()
    assert "In Review"   in transitions.keys()
    assert "Done"        in transitions.keys()
    assert jp.deleteIssue(issue_key)

def test_list_transitions_for_newly_created_issue_by_regular():
    """
        list transitions that an newly created issue can use 
        with getTransitions as a regular user
    """
    jp = JiraProxy(CONFIG_3)
    work_item = {"Summary" :  "Elitch Gardens is just OK."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    transitions = jp.getTransitions(issue_key)
    # If the PROJECT_KEY_4 is used the following lines would work
    #assert "Start Progress"  in transitions.keys()
    #assert "Resolve Issue"   in transitions.keys()
    #assert "Start Progress"  in transitions.keys()
    assert "To Do"       in transitions.keys()
    assert jp.deleteIssue(issue_key)

def test_transition_newly_created_issue_to_in_progress_state():
    """
        transition a newly created issue to the In Progress state
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Roller Coaster assembly point"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    # If the PROJECT_KEY_4 is used the following line would work
    #assert "Start Progress"  in transitions.keys()
    jp.transitionIssueState(issue_key, "In Progress")
    issue = jp.getIssue(issue_key)
    assert issue.Status == "In Progress"
    assert jp.deleteIssue(issue_key)

def test_transition_newly_created_issue_to_closed_state_in_restricted_workflow():
    """
        transition a newly created issue to the Closed state in restricted workflow
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Hand Grenades and horseshoes"}
    issue_key = jp.createIssue(PROJECT_KEY_4, "Bug", work_item)

    jp.transitionIssueState(issue_key, "Closed", "Won't Fix")
    issue = jp.getIssue(issue_key)
    assert issue.Status     == "Closed"
    assert issue.Resolution == "Won't Fix"
    assert jp.deleteIssue(issue_key)

def test_transition_issue_to_done_state():
    """
        transition a new issue to the Done state
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Roller Coaster assembly point"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    jp.transitionIssueState(issue_key,"Done" )
    issue = jp.getIssue(issue_key)
    assert issue.Status     == "Done"
    assert issue.Resolution == "Done"
    assert jp.deleteIssue(issue_key)

def test_transition_issue_to_done_state_and_wont_do_resolution():
    """
        transition issue to Done status and  Won't Do resolution
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Roller Coaster assembly point", "Resolution" :  "Won't Do"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    jp.transitionIssueState(issue_key,"Done" )
    issue = jp.getIssue(issue_key)
    assert issue.Status     == "Done"
    assert issue.Resolution == "Done"
    issue.Resolution = "Won't Do"
    success = jp.updateIssue(issue)
    if success:
        issue = jp.getIssue(issue.key)
    assert issue.Resolution == "Won't Do"
    assert jp.deleteIssue(issue_key)

def test_transition_newly_created_issue_to_resolved_state_with_a_resolution():
    """
        transition a newly created issue to the Resolved state with a resolution
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Roller Coaster assembly point"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    jp.transitionIssueState(issue_key, "Done")
    issue = jp.getIssue(issue_key)

    assert issue.Status     == "Done"
    assert issue.Resolution == "Done"
    assert jp.deleteIssue(issue_key)

def test_transition_new_issue_to_resolved_state_with_reso_in_restrictive_workflow():
    """
        transition a new issue to the Resolved state with a resolution in restrictive workflow
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Daytime TV spokesdroid says Be Sassy!"}
    issue_key = jp.createIssue(PROJECT_KEY_4, "Bug", work_item)
    jp.transitionIssueState(issue_key, "Resolved", "Cannot Reproduce")
    issue = jp.getIssue(issue_key)

    assert issue.Status     == "Resolved"
    assert issue.Resolution == "Cannot Reproduce"

    jp.transitionIssueState(issue_key, "Reopened")   # you can't actually get to Reopened, 
                                                     # but we don't die in the attempt
    assert issue.Status  == "Resolved"
    jp.transitionIssueState(issue_key, "Closed", "Fixed")
    issue = jp.getIssue(issue_key)
    assert issue.Status  == "Closed"
    jp.transitionIssueState(issue_key, "Reopened")
    issue = jp.getIssue(issue_key)
    assert issue.Status  == "Reopened"
    assert jp.deleteIssue(issue_key)

def test_transition_new_issue_to_resolved_state_without_resolution_in_restrictive_workflow():
    """
        transition a new issue to Resolved state without a resolution in restrictive workflow
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Don't be sassy with me!"}
    issue_key = jp.createIssue(PROJECT_KEY_4, "Bug", work_item)
    jp.transitionIssueState(issue_key, "Resolved")
    issue = jp.getIssue(issue_key)

    assert issue.Status == "Resolved"
    assert jp.deleteIssue(issue_key)

def test_transition_new_issue_to_Closed_state_without_resolution_in_restrictive_workflow():
    """
        transition a new issue to Closed state without a resolution in restrictive workflow
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Your life is an insult to the galaxy", "Severity" :  "Major Problem"}
    issue_key = jp.createIssue(PROJECT_KEY_4, "Bug", work_item)
    jp.transitionIssueState(issue_key, "Closed")
    issue = jp.getIssue(issue_key)
    assert issue.Status == "Closed"
    assert jp.deleteIssue(issue_key)

def test_resolution_attribute_uses_display_name_when_configured_to_use_custom_restictive_workflow():
    """
        Resolution attribute uses Display Name when Jira is configured to use a 
        custom workflow that is more restrictive than the simplified default workflow
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "Roller Coaster scream tester"}

    # In Jira 7 the following does not work as the simplified default workflow doesn't allow the transition to take place,
    # it returns an error whining about the Resolution not appearing on any screen or that the Resolution value is unrecognized.
    #issue_key = jp.createIssue(PROJECT_KEY_2, "Bug", work_item)
    #jp.transitionIssueState(issue_key, "Done", "Won't Do" )
    #issue = jp.getIssue(issue_key)
    # issue.Status.should == "Done"
    # issue.Resolution.should == "Won't Do"

    # So, we imported from Jira 6 a more restrictive workflow called 'Rally Workflow' (that we created back in 2012/2013)
    # and the following scenario passes in Jira 7.  We created a new Project (named in PROJECT_KEY_4) and associated
    # the workflow with that project.

    issue_key = jp.createIssue(PROJECT_KEY_4, "Bug", work_item)
    jp.transitionIssueState(issue_key, "Resolve Issue", "Won't Fix" )
    issue = jp.getIssue(issue_key)
    assert issue.Status     == "Resolved"
    assert issue.Resolution == "Won't Fix"
    assert jp.deleteIssue(issue_key)

def test_error_on_attempt_to_transition_new_issue_to_in_progress_state_with_a_resolution():
    """
        error out on an attempt transition a newly created issue to the 
        In Progress state with a resolution
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Roller Coaster assembly point"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    with py.test.raises(JiraProxyError) as excinfo:
        jp.transitionIssueState(issue_key, "In Progress", "Won't Do")
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'resolution' in actualErrorMessage
    assert jp.deleteIssue(issue_key)

def test_error_on_attempt_to_transition_new_issue_to_in_progress_state_with_invalid_resolution():
    """
        error out on an attempt transition a newly created issue to the 
           In Progress state with an invalid resolution
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_DEV_USER_CONFIG)
    work_item = {"Summary" :  "Roller Coaster Speed Test"}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    with py.test.raises(JiraProxyError) as excinfo:
        jp.transitionIssueState(issue_key, "Resolve Issue", "Too Slow")
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Transition action |Resolve Issue| not valid for issue' in actualErrorMessage
    assert jp.deleteIssue(issue_key)

def test_resolution_attribute_is_editable_for_issue_in_resolved_state():
    """
        Resolution attribute can be edited for an issue in the Resolved state
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "Roller Coaster scream tester"}
    issue_key = jp.createIssue(PROJECT_KEY_2, "Bug", work_item)
    issue = jp.getIssue(issue_key)

    issue.Status= "Done"
    issue.Resolution = "Done"
    jp.updateIssue(issue)

    assert issue.Status == "Done"
    #assert issue.Resolution == "Won't Do"
    assert issue.Resolution == "Done"

    issue["Resolution"] = "Won't Do"
    jp.updateIssue(issue)
    issue = jp.getIssue(issue_key)
    assert issue.Resolution == "Won't Do"
    assert jp.deleteIssue(issue_key)

def test_sad_raise_exception_when_action_not_available_for_the_issue():
    """
        should raise an exception if the action is not available for the issue"  do
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" :  "Roller Coaster scream tester"}
    issue_key = jp.createIssue(PROJECT_KEY_2, "Bug", work_item)

    no_action = "NonExistentAction"
    with py.test.raises(JiraProxyError) as excinfo:
        jp.getFieldsForAction(issue_key, no_action)
    actualErrorMessage = excErrorMessage(excinfo)
    assert  f"No transition named |{no_action}| allowed/found for issue" in actualErrorMessage

def test_sad_raise_exception_when_yet_another_action_not_available_for_the_issue():
    """
        should raise and exception if the action is not available for the issue"  do
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" : "Roller Coaster scream tester"}
    issue_key = jp.createIssue(PROJECT_KEY_2, "Bug", work_item)

    no_action = "Reopen Issue"
    with py.test.raises(JiraProxyError) as excinfo:
        jp.getFieldsForAction(issue_key, no_action)
    actualErrorMessage = excErrorMessage(excinfo)
    assert f"No transition named |{no_action}| allowed/found for issue" in actualErrorMessage


