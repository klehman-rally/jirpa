
import sys, os
import re
import base64
import uuid
import py

from jirpa import JiraProxy, JiraProxyError

##################################################################################################

from helper_pak import BasicLogger, excErrorMessage

from jira_targets import GOOD_VANILLA_ONDEMAND_REGULAR_USER_CONFIG

CLOUD_CONFIG = GOOD_VANILLA_ONDEMAND_REGULAR_USER_CONFIG

SMO_KEY_NAME  = 'SMO'
SMO_TEST_ITEM = 'SMO-1'

##################################################################################################

ATTACHMENT_FILE = os.path.join(os.path.dirname(__file__), "attachments", "attachment_for_test.txt")

def test_get_list_of_attachments_for_specific_issue():
    """
        get a list of attachments with the getIssueAttachmentsInfo method given an issue id
    """
    jp = JiraProxy(CLOUD_CONFIG)
    attachments = jp.getIssueAttachmentsInfo(SMO_TEST_ITEM)
    assert len(attachments) == 2
    matching_atts = [att for att in attachments if att.filename == 'earthjello.jpeg']
    assert len(matching_atts) >= 1
    image_attachment = matching_atts[0]
    assert image_attachment.filename == "earthjello.jpeg"
    assert image_attachment.mimetype == "image/jpeg"
    assert image_attachment.filesize == 43739


def test_get_the_attachment_content_for_an_issue_with_an_attachment():
    """
        should get the content of an attachment from an issue with an attachment
    """
    jp = JiraProxy(CLOUD_CONFIG)
    attachments = jp.getIssueAttachmentsInfo(SMO_TEST_ITEM)
    assert len(attachments) == 2

    matching_atts = [att for att in attachments if att.filename == 'testattachment.txt']
    assert len(matching_atts) >= 1
    text_attachment = matching_atts[0]
    assert text_attachment.filename == "testattachment.txt"
    content = jp.getAttachmentContent(text_attachment)
    assert content.decode('UTF-8') == "Hello World of hurt!"


def test_fail_gracefully_when_attempting_to_obtain_content_of_nonexistent_attachment():
    """
        should fail elegantly when attempting to retrieve the attachment 
        content of a non-existent attachment
    """
    jp = JiraProxy(CLOUD_CONFIG)
    attachments = jp.getIssueAttachmentsInfo(SMO_TEST_ITEM)
    acref = attachments[1].content_ref[:]
    acref = re.sub(r'attachment\/\d+\/', 'attachment/0000/', acref)
    attachments[1].content_ref = acref
    
    with py.test.raises(JiraProxyError) as excinfo:
        jp.getAttachmentContent(attachments[1])
    actualErrorMessage = excErrorMessage(excinfo)
    assert '404 (Not Found)' in actualErrorMessage


def test_adding_an_attachment_to_an_issue():
    """
        add an attachment to an issue
    """

    jp = JiraProxy(CLOUD_CONFIG)
    work_item = {"Summary" : "Monet was a painter"}
    issue_key = jp.createIssue(SMO_KEY_NAME, "Bug", work_item)
    attachments = []
    att_info  = {'filename'      : ATTACHMENT_FILE, 
                 'base64content' : base64.b64encode(open(ATTACHMENT_FILE, 'rb').read()), 
                 'mimetype'      : "text/plain"
                }
    attachments.append(att_info)
    result = jp.addAttachmentsToIssue(issue_key, attachments)
    assert result[ATTACHMENT_FILE]["added"] == True
    attachments = jp.getIssueAttachmentsInfo(issue_key)
    att_content = jp.getAttachmentContent(attachments[0])
    assert att_content.decode() == "The World is Good."

    assert jp.deleteIssue(issue_key)


def test_adding_an_attachment_using_connector_protocol():
    """
        add an attachment to an issue like from the connector
    """
    jp = JiraProxy(CLOUD_CONFIG)
    work_item = {"Summary" : "Monet was a painter"}
    issue_key = jp.createIssue(SMO_KEY_NAME, "Bug", work_item)
    attachments = []
    filename = f"attach-{uuid.uuid1()}.txt"
    file_content = base64.b64encode(b'Some text in the file')
    att_info  = {'filename' : filename, 'mimetype' : "text/plain", 'base64content' : file_content}
    attachments.append(att_info)
    result = jp.addAttachmentsToIssue(issue_key, attachments)
    assert result[filename]["added"] == True
    attachments = jp.getIssueAttachmentsInfo(issue_key)
    att_content = jp.getAttachmentContent(attachments[0])
    assert att_content.decode('UTF-8') == "Some text in the file"

    assert jp.deleteIssue(issue_key)

