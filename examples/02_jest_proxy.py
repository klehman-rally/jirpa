#!/usr/bin/env python
# Copyright 2021 Broadcom. All Rights Reserved.

##########################################################################################
#
#  02_jira_proxy.py - cycle over a list of Jira access configs and attempt to 
#                     obtain a JiraProxy instance for each config
#
##########################################################################################

from jirpa  import JiraProxy

SERVER_INSTANCE   = "http://10.23.22.11:8080"
ONDEMAND_INSTANCE = "https://alligator-tiers.atlassian.net" 


REG_USER = {
    'url'          :  SERVER_INSTANCE,
    'user'         :  "testuser",
    'password'     :  "jiradev"
   }

DEV_USER = {
    'url'         :  SERVER_INSTANCE,
    'user'        :  "devuser",
    'password'    :  "jiradev"
   }

NOPLACE_SERVER = {
    'url'         :  "http://noplace",
    'user'        :  "testuser",
    'password'    :  "testuser"
   }

NOUSER_CONFIG = {
    'url'         :  SERVER_INSTANCE,
    'user'        :  "nouser",
    'password'    :  "testuser"
   }

BADUSER_CONFIG = {
    'url'         :  SERVER_INSTANCE,
    'user'        :  "testuser",
    'password'    :  "badpw"
   }

JIRA_CONFIGS = [REG_USER, DEV_USER, NOPLACE_SERVER, NOUSER_CONFIG, BADUSER_CONFIG]

for jira_config in JIRA_CONFIGS:
    print(" ")
    print("-" * 80)
    print(" ")

    print(repr(jira_config))

    try:
        jira = JiraProxy(jira_config)
        if jira:
            print("    Obtained a JiraProxy instance")
        else:
            print("    Unable to obtain a JiraProxy instance")
    except Exception as exc:
        problem = exc.args[0]
        print(f"Error obtaining a JiraProxy instance: \n    {problem}")
    print("")

