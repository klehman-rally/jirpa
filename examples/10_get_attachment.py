#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  10_get_attachment.py - retrieve an attachment from an existing Jira issue
#
##########################################################################################

import sys
import time

from jirpa  import JiraProxy, JiraProxyError

##########################################################################################

SERVER_INSTANCE = "http://10.23.22.11:8080" # int-hobart in GCP saas-rally-dev-integrations

JIRA_REGULAR_USER_CONFIG = \
    {
     'user'       :  "testuser",
     'password'   :  "jiradev",
     'url'        :  SERVER_INSTANCE
    }

JIRA_ISSUE_KEY = "TST-3667"

##########################################################################################

def main(args):

    jira = JiraProxy(JIRA_REGULAR_USER_CONFIG)

    attachments = jira.getIssueAttachmentsInfo(JIRA_ISSUE_KEY)

    for attachment_info in attachments:
        content = jira.getAttachmentContent(attachment_info)
        print(f'{attachment_info.filename:<20} {attachment_info.mimetype:<12} Content length : {len(content)}')

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])

