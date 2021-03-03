
import sys, os
import py

from jirpa import JiraProxy, JiraProxyError

###############################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_SERVER_CONFIG

from jira_targets import PROJECT_KEY_1
from jira_targets import JEST_ISSUE_1_KEY

###############################################################################################

def test_get_comments_list_for_specific_issue_id():
    """
        get a list of comments with the getComments method given an issue id
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    comments = jp.getComments(JEST_ISSUE_1_KEY)
    assert len(comments) >= 2
    assert comments[0]["body"] == "A comment to be tested."


def test_use_addComment_method_for_specific_issue():
    """
        should be able to add a comment with the addComment method 
        given an issue id and comment text
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" : "Comments about games."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    comment_1 = "Foursquare is a great game"

    jp.addComment(issue_key, comment_1)
    comments = jp.getComments(issue_key)
    assert len(comments) == 1
    assert comments[0]["body"] == comment_1

    assert jp.deleteIssue(issue_key)


def test_add_two_comments_to_an_issue():
    """
        should be able to add two comments with the addComment method 
        given an issue id and comment text
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" : "Comments about games."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    comment_1 = "Foursquare is a great game"
    comment_2 = "Risk is a fun board game"

    jp.addComment(issue_key, comment_1)
    jp.addComment(issue_key, comment_2)
    comments = jp.getComments(issue_key)
    assert len(comments) == 2
    assert comments[0]["body"] == comment_1
    assert comments[1]["body"] == comment_2


def test_decent_error_message_for_getComments_when_issue_key_nonexistent():
    """
        Error message should be useful when key does nt exist in getComments
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" : "Comments about games."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    jp.deleteIssue(issue_key)

    with py.test.raises(JiraProxyError) as excinfo:
       jp.getComments(issue_key)
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Issue Does Not Exist' in actualErrorMessage


def test_decent_error_message_for_addComments_when_issue_key_nonexistent():
    """
        Error message should be useful when key does not exist in addComments.
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" : "Comments about games."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)
    assert jp.deleteIssue(issue_key)

    comment_1 = "Foursquare is a great game"
    with py.test.raises(JiraProxyError) as excinfo:
        jp.addComment(issue_key, comment_1)
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Issue Does Not Exist' in actualErrorMessage


def test_disallow_adding_a_blank_comment():
    """
        should be not be able to add a blank comment with the addComment method.
    """
    jp = JiraProxy(GOOD_VANILLA_SERVER_CONFIG)
    work_item = {"Summary" : "Comments about games."}
    issue_key = jp.createIssue(PROJECT_KEY_1, "Bug", work_item)

    comment_1 = ""
    with py.test.raises(JiraProxyError) as excinfo:
        jp.addComment(issue_key, comment_1)
    actualErrorMessage = excErrorMessage(excinfo)
    assert 'Comment body can not be empty!' in actualErrorMessage
    assert jp.deleteIssue(issue_key)

