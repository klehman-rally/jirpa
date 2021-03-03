
import sys, os
import py

from jirpa import JiraProxy, JiraProxyError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG, 
from jira_targets import PROJECT_KEY_5 as AGL_PROJECT

###############################################################################################

issue_key_patt = re.compile(f'^{AGL_PROJECT}-\\d+')


#def test_create_jira_issue_with_valid_sprint_id():
#    """
#       create a JIRA issue with a valid Sprint field id
#    """
#    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
#
#    work_item = {"Summary"  : "Usain Bolt does not slow down for anything",
#                 "Reporter" : "testuser",
#                 "Assignee" : "devuser",
#                 "Sprint"   : 1   # 1 is the ID for the Sprint value of "AGL Sprint 1"
#                }
#
#    issue_key = jp.createIssue(AGL_PROJECT, "Story", work_item)
#    assert issue_key_patt.match(issue_key)
#    story = jp.getIssue(issue_key)
#    assert story.Sprint == '1'
#    jp.deleteIssue(issue_key)

#
#def test_sad_graceful_fail_on_attempt_to_create_issue_with_invalid_sprint_value():
#    """
#       gracefully fail on an attempt to create a JIRA Story with a non-valid Sprint value
#    """
#    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
#    work_item = {"Summary" :  "Recombinant DNA faulty with respect to distal remortix",
#                 "Sprint"  :  329007 
#                }
#    with py.test.raises(JiraProxyError) as excinfo:
#        jp.createIssue(AGL_PROJECT, "Story", work_item)}
#    actualErrorMessage = excErrorMessage(excinfo)
#    assert 'Sprint does not exist' in actualErrorMessage

#def test_update_existing_jira_story_with_sprint_not_currently_populated():
#    """
#        update a JIRA Story with the Sprint field not already populated
#    """
#    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
#
#    work_item = {"Summary"  :  "The Brazilian soccer leagues are mean spirited",
#                 "Reporter" :  "testuser",
#                 "Assignee" :  "devuser",
#                }
#    issue_key = jp.createIssue(AGL_PROJECT, "Story", work_item)
#    issue = jp.getIssue(issue_key)
#
#    issue.Sprint = 1
#
#    updated = jp.updateIssue(issue)
#    assert updated == True
#    issueAgain = jp.getIssue(issue_key)
#    assert issueAgain.key    == issue_key
#    assert issueAgain.Sprint == '1'
#    jp.deleteIssue(issue_key)


#def test_update_existing_jira_story_with_sprint_already_populated():
#    """
#       update a JIRA Story with the Sprint field already populated with a Sprint ID
#    """
#    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
#    work_item = {"Summary"   : "street sweeping utilites move lots of dust",
#                 "Reporter"  : "testuser",
#                 "Assignee"  : "devuser",
#                 "Sprint"    : 1
#                }
#
#    issue_key = jp.createIssue(AGL_PROJECT, "Story", work_item)
#    issue = jp.getIssue(issue_key)
#    issue.Sprint = 2
#    issue = jp.updateIssue(issue)
#    updated_issue = jp.getIssue(issue_key)
#    assert updated_issue.Sprint == "2"
#    jp.deleteIssue(issue_key)


