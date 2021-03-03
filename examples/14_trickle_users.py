#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  14_trickle_users.py - show the users in a Jira instance
#
##########################################################################################

import sys
sys.path.append("test")

from jirpa  import JiraProxy, JiraProxyError

from jira_targets import GOOD_VANILLA_ONDEMAND_CONFIG

##########################################################################################

def main(args):

    jira = JiraProxy(GOOD_VANILLA_ONDEMAND_CONFIG)
    for user in jira.getAllUsers():
        print(user.info())

##########################################################################################
##########################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])

