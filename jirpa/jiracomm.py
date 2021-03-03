# jiracomm file for jirpa package

import os
import json
import re
from requests.utils import requote_uri
import base64  # is this needed for attachments?  maybe not here but in jiraproxy.py

import requests

from .mutelogger import MuteLogger

###################################################################################

class JiraCommError(Exception): pass

class JiraComm:

    def __init__(self, config):
        self.url            = config.get('url')  # like http://<IPADDR||SERVER>{:<PORT>}
        self.user           = config.get('user')
        self.accountId      = config.get('accountId')
        self.password       = config.get('password')
        self.proxies        = None  # only gets set if there is a proxy_url config item
        self.proxy_url      = config.get('proxy_url',  None)
        self.proxy_user     = config.get('proxy_user', None)
        self.proxy_password = config.get('proxy_password', None)
        self.verify_cert    = config.get('verify_cert', False)
        self.timeout        = config.get('timeout', 30) 
        self.logger         = config.get('logger', MuteLogger())
        self.on_demand      = False  # default to this, it gets reset to true later depending on the self.url value
        log = self.logger

        self.jira_url_prefix = f'{self.url}/rest/api/2'
        self.basic_auth = requests.auth.HTTPBasicAuth(self.user, self.password)
        self.auth = self.basic_auth

        if not self.proxy_url:
            if not self.proxy_user:
                warning = "Proxy user has been configured, but Proxy URL has not been configured"
                log.warn(warning)
        else:
            log.info(f"jirpa JiraComm using proxy: |{self.proxy_url}|")
            target_protocol = self.url.split(':', 1)[0]
            self.proxies = {target_protocol : self.proxy_url}
            if not self.proxy_user:
                log.info("No credentials for proxy server configured")
            else:
                log.info(f"jirpa JiraComm proxy user: |{self.proxy_user}|")
                if not self.proxy_password:
                    log.info("Proxy password has NOT been configured")
                else:
                    log.info("Proxy password has been configured")

        self.conn = requests.Session()

        options = {'username' : self.user, 'password' : self.password}
        if re.search(r'\.atlassian\.net', self.url, re.IGNORECASE):
            if self.accountId is None or not self.accountId:
                problem = (f"Jira OnDemand REST API requires the use "
                           f"of the accountId of the target user")
                raise JiraCommError(problem)
            self.on_demand = True
            options = {'accountId' : self.accountId}

        status, result, errors = self.getRequest('user', **options)
        self.status = status
        self.result = result
        self.errors = errors
        if status != 200:
            #print(f"Initial connection status code: {status}  errors: {errors}")
            raise JiraCommError(f"Unable to connect to {self.url}")


    def executeRequest(self, method, target, payload=None, extra_headers=None, **option):
        """
        """
        if option.get('verbatim_url', False):
            endpoint = target
            del option['verbatim_url'] # so this doesn't get appened as query string arg
        else:
            endpoint = f"{self.jira_url_prefix}/{target}"
        self.logger.debug(f"issuing a {method.upper()} request for endpoint: {endpoint}")

        if option:
            kv_pairs = [requote_uri(f"{key}={value}") for key,value in option.items()]
            query_string = "&".join(kv_pairs)
            #print(f"query_string: {query_string}")
            endpoint += f"?{query_string}"
        #print(f"executeRequest on endpoint: {endpoint}")
        #if payload: payload = json.dumps(payload)  # (*maybe don't need to do this since requests.post
        #                                        # takes the dict directly as the data keyword arg...
        """
          the following have to be used in the executeRequest upon calling
          self.conn.<operation> (get, put, post, delete)

          url encoded    -  taken care of with the requote_uri above for the query_string
          timeout - not subdivided by the following  (but would be in **option parameter dict)
          verify  parm is from self.verify_cert (False by default, can be set from init config)
          proxies parm is from self.proxies (None by default, has value according to self.proxy_url)
              {'http'  : 'foo.bar:3128', 
               'https' : 'gatorious.atlassian.net:3128',
               'http://host.name': 'foo.bar:4012'
              }
        """
        if not extra_headers:
            extra_headers = {}
        if 'Content-Type' not in extra_headers:
            extra_headers['Content-Type'] = 'application/json'
        if 'X-Atlassian-Token' not in extra_headers:
            extra_headers['X-Atlassian-Token'] = 'nocheck'
        if extra_headers.get('Content-Type', 'application/json') == 'application/json':
            if payload:
                payload = json.dumps(payload)

        response = self.conn.request(method, endpoint, auth=self.auth, 
                                     headers=extra_headers, 
                                     data=payload,
                                     timeout=option.get('timeout', 20),
                                     proxies=self.proxies,
                                     verify=self.verify_cert
                                    )
        try:
            payload = json.dumps(response.json(), indent=4)
            #if payload: self.logger.debug(payload)
        except Exception as exc:
            pass

        return self.parseResponse(endpoint, response)


    def getRequest(self, target, **option):
        return self.executeRequest('GET', target, **option)

    def postRequest(self, target, data, extra_headers=None):
        return self.executeRequest('POST', target, payload=data, extra_headers=extra_headers)

    def putRequest(self, target, data, extra_headers=None):
        return self.executeRequest('PUT', target, payload=data, extra_headers=extra_headers)

    def deleteRequest(self, target, **option):
        return self.executeRequest('DELETE', target, **option)

    
    def parseResponse(self, endpoint, response):
        """
        """
        result, errors = response, None
        if response.content:
            try:
                result = response.json()
            except Exception as exc:
                pass
        if not 200 <= response.status_code <= 299:
            errors = f"Response code for {endpoint} was {response.status_code} "
        if response.status_code == 401:
            errors = f"Response code for {endpoint} was 401 (Unauthorized) "
        if result and 'errorMessages' in result:
            errors = "\n".join(result['errorMessages'])
            if 'errors' in result:
                errors += repr(result['errors'])

        return response.status_code, result, errors


    def getAttachment(self, att_info):
        """
        """
        att_content_url = att_info.content_ref
        extra_headers = {'Content-Type' : att_info.mimetype}
        options = {'verbatim_url' : True}

        status, response, errors \
                = self.executeRequest('GET', att_content_url, 
                                      extra_headers=extra_headers, 
                                      **options)

        
        if status == 302:
            redirect_url = response.headers['location']
            status, response, errors \
                = self.executeRequest('GET', redirect_url, 
                                      extra_headers=extra_headers, 
                                      **options)

        errors = None
        if not 200 <= status <= 299:
            errors = f"Response code for {att_content_url} was {status} "

        if status == 401:
            errors = f"Response code for {att_content_url} was 401 (Unauthorized) "

        if status == 404:
            errors = f"Response code for {att_content_url} was 404 (Not Found) "

        if response.content:
            attachment_content = response.content
        else:
            attachment_content = None

        return status, attachment_content, errors


    def postAttachment(self, issue_key, att_info):
        """
        """
        import binascii

        filename = att_info['filename']
        mimetype = att_info['mimetype']
        fileio   = att_info['file_content']
        file_base_name = os.path.basename(filename)

        boundary = binascii.hexlify(os.urandom(16)).decode('ascii')
        separator = "\r\n"   #CRLF used as separator for elements in multipart/form-data
        # multipart/form-data consists of:
        # prefix
        # file contents
        # suffix
        prefix =  f'--{boundary}{separator}'
        prefix += f'Content-Disposition: form-data; name="file"; filename="{file_base_name}"{separator}'
        prefix += f'Content-Type: application/octet-stream{separator}{separator}'
        suffix =  f'{separator}--{boundary}--{separator}'

        # convert the prefix and suffix to binary and then join them around the binary contents of the file
        parts = [part.encode('UTF-8') for part in [prefix, att_info['file_content'], suffix]]
        payload = b''.join(parts)
        extra_headers = {'Content-Type'   : f'multipart/form-data; boundary={boundary}',
                         'Content-Length' : str(len(payload))
                        }
        att_url = f'{self.jira_url_prefix}/issue/{issue_key}/attachments'
        options = {'verbatim_url' : True}
        status, response, errors \
            = self.executeRequest('POST', att_url,
                                  extra_headers=extra_headers,
                                  payload=payload,
                                  **options)
        # contemplate checking status code here and raising exception for non 2xx level code
        return status, response, errors
