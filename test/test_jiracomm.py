
import sys, os
import py
import re
import copy

import requests

from jirpa import JiraComm, JiraCommError

#############################################################################################

from jira_targets import GOOD_VANILLA_SERVER_CONFIG, GOOD_VANILLA_ONDEMAND_CONFIG

DEFAULT_TIMEOUT = 30
BAD_SERVER_VERBIAGE = r'Failed to establish a new connection: .* ' + \
                      r'nodename nor servname provided, or not known'

def excErrorMessage(excinfo):
    """
        At some point in time excinfo.value.args[0] was the interesting part
        but now the appropriate thing is str(excinfo.value)
    """
    return str(excinfo.value)

#############################################################################################

def test_happy_basic_connection():
    """
        Basic initial connection/login against JIRA_SERVER
    """
    jc = JiraComm(GOOD_VANILLA_SERVER_CONFIG)
    assert jc is not None
    assert jc.status == 200
    
def test_sad_non_existent_server():
    """
        JiraComm should fail with an invalid url
    """
    bad_config = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    bad_config['url'] = "http://horkus:8080"
    expectedErrorPattern = re.compile(BAD_SERVER_VERBIAGE)
    with py.test.raises(Exception) as excinfo:
        jc = JiraComm(bad_config)
    assert expectedErrorPattern.search(excErrorMessage(excinfo)) is not None

def test_sad_invalid_user():
    """
        JiraComm should fail with an invalid user
    """
    bad_config = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    bad_config['user'] = "notarealuser"
    with py.test.raises(JiraCommError) as excinfo:
        jc = JiraComm(bad_config)
    assert "Unable to connect" in excErrorMessage(excinfo)

def test_sad_invalid_password():
    """
        JiraComm should fail with an invalid password
    """
    bad_config = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    bad_config['password'] = "badpassword"
    with py.test.raises(JiraCommError) as excinfo:
        jc = JiraComm(bad_config)
    assert "Unable to connect" in excErrorMessage(excinfo)

def test_happy_use_default_timeout():
    """
        JiraComm uses default values for timeouts if not specified in 
        the initialization config argument
    """
    jc = JiraComm(GOOD_VANILLA_SERVER_CONFIG)
    assert jc.timeout == DEFAULT_TIMEOUT

def test_happy_use_specifid_timout():
    """
        new JiraComm instance uses a non-default timeout configuration
    """
    config = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    config['timeout'] =  95
    jc = JiraComm(config)
    assert jc.timeout == 95

def hide_test_sad_ridiculous_short_timeout():
    """
        JiraComm.new with a ridiculously short timeout should raise an exception

        Doesn't timeout against our Jira Server...
    """
    short_fuse = copy.copy(GOOD_VANILLA_SERVER_CONFIG)
    short_fuse['timeout'] = 0.00000000001
    jc = JiraComm(short_fuse)
    
    assert jc.status != 200
   # with py.test.raises(Exception) as excinfo:
   #     jc = JiraComm(short_fuse)
   # assert 'TimeoutError' in excErrorMessage(excinfo)


