
import sys, os
import json
import base64
import copy
import re
import traceback

from .mutelogger import MuteLogger
from .jiracomm   import JiraComm
from .entities   import JiraServerInfo, JiraUser, JiraFieldSchema, JiraAttachmentMeta
from .jiraissue  import JiraIssue

##################################################################################################

class JiraProxyError(Exception): pass

class JiraProxy:

    def __init__(self, config={}):

        for option in ['url', 'user', 'password']:
            if option not in config:
                raise JiraProxyError(f"JiraProxy requires the config item for {option} to be present")

        self.logger = config.get('logger', MuteLogger())
        password_less_config = copy.copy(config)
        password_less_config['password'] = "*****"
        password_less_config['proxy_password'] = "*****"
        self.logger.debug(f'JiraProxy config arg content: {repr(password_less_config)}')
        self.jira_comm = JiraComm(config)
        self.jira_user = config['user']

        self.project_info   = None
        self.issue_types    = []
        self.issue_type_map = {}
        self.issue_type_id_for_name = {}
        #
        # *_fields dict contains the field attributes returned by jira using createmeta and editmeta
        # *_field_names is a list of the valid field names that the user can use with issue. or issue[]
        #
        # these next 4 dicts are keyed at first  level by project key
        #                              at second level by issue_type(name)
        self.standard_fields      = {}
        self.custom_fields        = {}
        self.standard_field_names = {}
        self.custom_field_names   = {}

        self.action_fields    = {}  # keyed by an action_id,
                                    # value is a list of fields valid for updating as part of the action
        self.project_versions = {}  # key at first level by project_key, 
                                    # associated value is list of versions
        self.status_values           = []
        self.status_value_for_id     = {}
        self.priority_values         = []
        self.priority_value_for_id   = {}
        self.resolution_values       = []
        self.resolution_value_for_id = {}

        self.jira_version = self.getServerInfo()

        self.getIssueTypes()
        self.getStatuses()
        self.getPriorities()
        self.getResolutions()


    def getProjects(self):
        if self.project_info:
            return self.project_info
        endpoint = 'project'
        status, result, errors = self.jira_comm.getRequest(endpoint)
        if errors:
            raise JiraProxyError(errors)

        # populate a dict of project_key to project name mappings in 
        # the self.project_info instance variable
        self.project_info = {}
        for proj in result:
            self.project_info[proj["key"]] = proj["name"]
        return self.project_info


    def getProjectsDetails(self):
        proj_list = self.getProjects()
        details_list = []
        for proj_key, proj_name in proj_list.items():
            endpoint = f'project/{proj_key}'
            status, full_proj, errors = self.jira_comm.getRequest(endpoint)
            if errors:
                raise JiraProxyError(errors)
            proj_desc = full_proj["description"]
            proj_pak = { "Key"  :  proj_key, 
                         "Name" :  proj_name, 
                         "Description" :  proj_desc, 
                         "Details" :  full_proj
                       }
            details_list.append(proj_pak)
        return details_list


    def getServerInfo(self):
        # needs to pass back an instance with attr_readers for popular attributes
        # including version
        endpoint = 'serverInfo'
        status, result, errors = self.jira_comm.getRequest(endpoint)
        if errors:
            raise JiraProxyError(errors) 
        return JiraServerInfo(result)

    def getGroups(self, username):
        # obtain the group memberships for a specific user
        criteria = {'username' :  username,  'expand': 'groups'}
        endpoint = 'user'
        status, result, errors = self.jira_comm.getRequest(endpoint, **criteria)

        self.logger.debug(f"getGroups return code {status}")

        if errors:
            self.logger.debug(f"getGroups errors : {errors}")
            raise JiraProxyError(errors)
        if "groups" not in result:
            error_message =  f' .getGroups error message: no groups entry for user: {username}'
            raise JiraProxyError(error_message)
        found_groups = [item["name"] for item in result["groups"]["items"]]
        return found_groups


    def getUsers(self, project, start_at=0, limit=1000):
        project_key = self._getProjectKey(project)
        all_users = []
        endpoint = "user/assignable/search"
        options = { "project"    : project_key,
                    "startAt"    : start_at,
                    "maxResults" : limit
                  }
        rounds = 0
        jira_max_result_block_size = 1000
        while True:
            options['startAt'] = rounds * jira_max_result_block_size
            status, result, errors = self.jira_comm.getRequest(endpoint, **options)
            if errors:
                raise JiraProxyError(errors)
            users = [JiraUser(item) for item in result]
            all_users.extend(users)
            rounds +=1

            if len(users) < jira_max_result_block_size:
                break

        return all_users

    getAssignableUsers = getUsers


    def getUsersMatching(self, target):
        endpoint = "user/search"
        options = { "username"        :  "%s" % target,
                    "startAt"         :  0,
                    "maxResults"      :  1000,
                    "includeInactive" :  True
                  }
        status, result, errors = self.jira_comm.getRequest(endpoint, **options)
        return status, result, errors


    def getAllUsers(self):
        all_users = []
        seen = {}
        alphanum = "abcdefghijklmonopqrstuvwxyz0123456789"
        #for character in alphanum.split(''):
        for character in alphanum:
            status, result, errors = self.getUsersMatching(character)
            for user_item in result:
                user_name = user_item["name"]
                if user_name not in seen:
                    seen[user_name] = True
                    all_users.append(JiraUser(user_item))
        return all_users


    def getIssueTypes(self):
        # instance wide info, across all projects
        if not self.issue_type_map:
            endpoint = 'issuetype'
            status, results, errors = self.jira_comm.getRequest(endpoint)
            for entry in results:
                name = entry["name"]
                self.issue_types.append(name)
                self.issue_type_map[name] = entry
                self.issue_type_id_for_name[name] = int(entry["id"])
        return self.issue_types, self.issue_type_map


    def _buildMapFromResult(self, result):
        # build a map (dict) with each item's id as the key mapping to item's value
        ident_map = {}
        for item in result:
            ident_map[item["id"]] = item["name"]
        return ident_map


    def getStatuses(self):
        if not self.status_values:
            endpoint = 'status'
            status, result, errors = self.jira_comm.getRequest(endpoint)
            self.status_value_for_id = self._buildMapFromResult(result)
            #result.each do | entry | self.status_values << entry["name"] end
            self.status_values = [entry["name"] for entry in result] 
        return self.status_values

    def getPriorities(self):
        if not self.priority_values:
            endpoint = 'priority'
            status, result, errors = self.jira_comm.getRequest(endpoint)
            self.priority_value_for_id = self._buildMapFromResult(result)
            #result.each do | entry | self.priority_values << entry["name"] end
            self.priority_values = [entry["name"] for entry in result]
        return self.priority_values

    def getResolutions(self):
        if not self.resolution_values:
            endpoint = 'resolution'
            status, result, errors = self.jira_comm.getRequest(endpoint)
            self.resolution_value_for_id = self._buildMapFromResult(result)
            #result.each do | entry | self.resolution_values << entry["name"] end
            self.resolution_values = [entry["name"] for entry in result]
        return self.resolution_values


    def getCustomFields(self, project, issue_type):
        project_key = self._getProjectKey(project)
        if issue_type not in self.issue_types:
            it_list = ", ".join(self.issue_types)
            problem = f'bad issue type: |{issue_type}|, valid issue types are: {it_list}'
            raise JiraProxyError(problem)

        if project_key not in self.custom_fields:
            self.custom_fields[project_key] = {}
            self.custom_field_names[project_key] = {}
        if issue_type not in self.custom_fields[project_key]:
            self._getFields(project_key, issue_type)
        return self.custom_field_names[project_key][issue_type]
    

    def getStandardFields(self, project, issue_type):
        project_key = self._getProjectKey(project)
        if issue_type not in self.issue_types:
            it_list = ", ".join(self.issue_types)
            problem = f'bad issue type: |{issue_type}|, valid issue types are: {it_list}'
            raise JiraProxyError(problem)

        if project_key not in self.standard_fields:
            self.standard_fields[project_key] = {}
            self.standard_field_names[project_key] = {}
        if issue_type not in self.standard_fields[project_key]:
            self._getFields(project_key, issue_type)
        return self.standard_field_names[project_key][issue_type]


    def fieldExists(self, project, issue_type, field_name):
        if issue_type not in self.issue_types:
            it_list = ", ".join(self.issue_types)
            problem = f'bad issue type: |{issue_type}|, valid issue types are: {it_list}'
            raise JiraProxyError(problem)


        if field_name.lower() == 'key':  # special case, the 'key' field is handled differently
            return True 
        if field_name.lower() == 'status':
            return True 
        if field_name.lower() == 'resolution':
            return True 
        if re.search(r'created|createddate|created date', field_name.lower()):
            return True 
        if re.search(r'updated|updateddate|updated date', field_name.lower()):
            return True 

        standard_field_names = self.getStandardFields(project, issue_type)
        hit = [fn.lower() for fn in standard_field_names if fn.lower() == field_name.lower()]
        if hit:
            return True

        custom_field_names = self.getCustomFields(project, issue_type)
        hit = [fn.lower() for fn in custom_field_names if fn.lower() == field_name.lower()]
        if hit:
            return True

        return False


    def fieldSchema(self, project, issue_type, field_name):
        project_key = self._getProjectKey(project)

        if issue_type not in self.issue_types:
            it_list = ", ".join(self.issue_types)
            problem = f'bad issue type: |{issue_type}|, valid issue types are: {it_list}'
            raise JiraProxyError(problem)
        if not self.fieldExists(project_key, issue_type, field_name):
            problem = (f'No such field {field_name} exists for project {project_key} '
                       f'and issue type {issue_type}')
            raise JiraProxyError(problem)
        custom = False
        if self.isCustomField(project_key, issue_type, field_name):
            info = self.custom_fields[project_key][issue_type][field_name]
            custom = True
        else:
            info = self.standard_fields[project_key][issue_type][field_name]

        return JiraFieldSchema(info, not custom, custom)


    def isCustomField(self, project, issue_type, field_name):
        if issue_type not in self.issue_types:
            it_list = ", ".join(self.issue_types)
            problem = f'bad issue type: |{issue_type}|, valid issue types are: {it_list}'
            raise JiraProxyError(problem)

        custom_fields = self.getCustomFields(project, issue_type)
        #hit = custom_fields.find {|fn| fn.downcase == field_name.to_s.downcase}
        hit = [fn for fn in custom_fields if  fn.lower() == field_name.lower()]
        if hit:
            return True

        return False


    def _getFields(self, project, issue_type_name):
        # get field info for project_key issue_type and populate 
        #  self.standard_fields and self.custom_fields
        # eg., self.standard_fields[project_key][issue_type] = ...
        # eg., self.custom_fields  [project_key][issue_type] = ...
        project_key = self._getProjectKey(project)
        options = {}
        options["projectKeys"]    = project_key
        options["issuetypeNames"] = issue_type_name
        options["expand"]         = "projects.issuetypes.fields"
        endpoint = 'issue/createmeta'
        status, field_info, errors = self.jira_comm.getRequest(endpoint, **options)
        if errors:
            problem = f'Failed issue/createmeta query for {project_key} {issue_type_name}, {errors}'
            raise JiraProxyError(problem)

        try:
            schema_info = json.dumps(json.loads(field_info, indent=4))
        except Exception as ex:
            schema_info = field_info
        self.logger.debug(f"field_info returned from JIRA options-{options} were:\n{schema_info}")
        
        project_1 = field_info['projects'][0]  # should be only 1 item in field_info['projects'] list
        if not project_1['issuetypes']:
            problem = (f'Could not find Issue Type "{issue_type_name}" in Project "{project}".  '
                       f'Ensure the Issue Type "{issue_type_name}" is available '
                       f'(via Project -> Administration -> Issue Types ...)')
            raise JiraProxyError(problem)

        issue_type_info = field_info['projects'][0]['issuetypes'][0]
        fields = issue_type_info["fields"]
        self.record_fields(project_key, issue_type_name, fields, "create")

        # get an issue (any issue will do) for the project_key and issue_type_name
        search_options = \
            {
             'jql'        :  f"project = {project_key} AND issuetype = '{issue_type_name}'",
             'startAt'    :  0,
             'maxResults' :  1,
             'fields'     :  "*all"
            }
        endpoint = 'search'
        status, result, errors = self.jira_comm.getRequest(endpoint, **search_options)
        if errors:
            problem = f'Failed issue search query: {search_options[:jql]}, {errors}'
            raise JiraProxyError(problem)

        # use the issue_key from the result as the issue_key 
        # in a issue/#{issue_key}/editmeta REST call
        if result["total"] > 0:
            issue_key = result['issues'][0]["key"]
            endpoint = f'issue/{issue_key}/editmeta'
            status, field_info, errors = self.jira_comm.getRequest(endpoint, **options)
            if errors:
                problem = f'Failed {endpoint} query for {project_key} {issue_type_name}, {errors}'
                raise JiraProxyError(problem)
            fields = field_info['fields']
            self.record_fields(project_key, issue_type_name, fields, "edit")


    def record_fields(self, project_key, issue_type_name, fields, mode):
        """
            record as in verb (RE-cord)
        """
        if project_key not in self.standard_fields:
            self.standard_fields[project_key]      = {}
            self.standard_field_names[project_key] = {}
        if issue_type_name not in self.standard_fields[project_key]:
            self.standard_fields[project_key][issue_type_name] = {}
        self.standard_field_names[project_key][issue_type_name] = []
        standard_field_keys = [name for name in fields.keys() if not name.startswith("customfield")]
        for key in standard_field_keys:
            field_name = fields[key]["name"]
            if field_name not in self.standard_fields[project_key][issue_type_name]:
                self.standard_fields[project_key][issue_type_name][field_name] = {}
            self.standard_fields[project_key][issue_type_name][field_name][mode] = fields[key]
            self.standard_field_names[project_key][issue_type_name].append(field_name)
        unique_list = list(set(self.standard_field_names[project_key][issue_type_name]))
        self.standard_field_names[project_key][issue_type_name] = unique_list[:]

        if project_key not in self.custom_fields:
            self.custom_fields[project_key]      = {}
            self.custom_field_names[project_key] = {}
        if issue_type_name not in self.custom_fields[project_key]:
            self.custom_fields[project_key][issue_type_name] = {}
        self.custom_field_names[project_key][issue_type_name] = []
        custom_field_keys = [name for name in fields.keys() if name.startswith("customfield")]
        for key in custom_field_keys:
            field_name = fields[key]["name"]
            if field_name not in self.custom_fields[project_key][issue_type_name]:
                self.custom_fields[project_key][issue_type_name][field_name] = {}
            self.custom_fields[project_key][issue_type_name][field_name][mode] = fields[key]
            self.custom_field_names[project_key][issue_type_name].append(field_name)
        unique_list = list(set(self.custom_field_names[project_key][issue_type_name]))
        self.custom_field_names[project_key][issue_type_name] = unique_list


    def createIssue(self, project, issue_type, work_item):
        project_key = self._getProjectKey(project)
        if issue_type not in self.issue_types:
            it_list = ", ".join(self.issue_types)
            problem = f'bad issue type: |{issue_type}|, valid issue types are: {it_list}'
            raise JiraProxyError(problem)

        jira_item = {"key"     :  f"{project_key}-0000",
                     "fields"  :  work_item
                    }
        jira_item["fields"]["issuetype"] = {"name" :  issue_type}
        issue = self.makeAnIssueInstance(jira_item)
        postable_issue_data = issue.jiralize('create')
        self.logger.debug(f"will create a JIRA issue with:  {postable_issue_data}")
        status, issue, errors = self.jira_comm.postRequest("issue", postable_issue_data)

        if errors:
            problem = (f'Creating issue type {issue_type} in project {project_key} '
                       f'failed: {errors}')
            raise JiraProxyError(problem)

        return issue["key"]  # just the key not the whole issue


    def getIssue(self, issue_key):
        endpoint = f'issue/{issue_key}'
        status, jira_item, errors = self.jira_comm.getRequest(endpoint)
        self.logger.debug(f"getIssue({issue_key}) returned status of {status}")
        if errors:
            self.logger.error(f'getIssue({issue_key}) returned {errors}')
            raise JiraProxyError(errors)

        ## TODO make sure you don't create an issue for a result that is "empty"
        jira_issue = None
        if 200 <= status <= 299:
            jira_issue = self.makeAnIssueInstance(jira_item)
        return jira_issue


    def getIssuesWithJql(self, jql_query, fields=None, start_at=0, limit=1000):

        # There are six cases where Display Names need to be replaced  with jql field names:
        #   Affects Version/s   :   affectedVersion
        #   Fix Version/s       :   fixVersion
        #   Component/s         :   component
        #   Due Date            :   duedate
        #   Original Estimate   :   originalEstimate
        #   Remaining Estimate  :   remainingEstimate

        # Note that the Original Estimate and Remaining Estimate are not listed 
        # in either create meta or edit meta rest calls.

        self.logger.debug(f"Initial jql: {jql_query}")
        jql_query = jql_query.replace(r'Affects Version/s', "affectedVersion")
        jql_query = jql_query.replace(r'Fix Version/s',     "fixVersion")
        jql_query = jql_query.replace(r'Component/s',       "component")
        jql_query = jql_query.replace(r'Due Date',           "duedate")
        jql_query = jql_query.replace(r'Original Estimate',  "originalEstimate")
        jql_query = jql_query.replace(r'Remaining Estimate', "remainingEstimate")

        #
        # Fix for DE17360  - ampersand char (&) and plus symbol (+) must be urlencoded as unicode code point value
        #
        jql_query = jql_query.replace(r'&', '\\u0026')
        jql_query = jql_query.replace(r'+', '\\u002B')
        jql_query = jql_query.replace(r'%', '\\u0025')
        jql_query = jql_query.replace(r'?', '\\u003F')
        jql_query = jql_query.replace(r'@', '\\u0040')

        self.logger.debug(f"Updated jql: {jql_query}")

        search_options = {'jql'      :  jql_query,
                          'startAt'  :  start_at,
                          'fields'   :  "*all" if fields is None else fields,
                         }
        issues = []
        result = None
        errors = None
        endpoint = 'search'
        while True:
            status, result, errors = self.jira_comm.getRequest(endpoint, **search_options)
            if errors:
                raise JiraProxyError(errors)
            if not result:
                problem = (f'JQL search returned empty results: jql: {jql_query}  '
                           f'startAt: {search_options[startAt]}')
                raise JiraProxyError(problem)

            issues.extend([self.makeAnIssueInstance(jira_item) 
                                 for jira_item in result["issues"]])

            start_at += result["maxResults"]
            search_options['startAt'] = start_at

            if len(issues) >= result["total"] or len(issues) >= limit:
                break

        return issues


    def updateIssue(self, issue):
        putable_data = issue.jiralize('edit')
        self.logger.debug(f'before call to update {issue["key"]} with {repr(putable_data)}')
        status, result, errors = self.jira_comm.putRequest(f"issue/{issue.key}", putable_data)
        self.logger.debug(f'status, result, errors from update call: {status} <-> {result} <-> {errors}')
        if errors:
            supplied_update_info = repr(putable_data["fields"])
            problem = (f'JIRA update errors for {issue.key} {errors}, '
                       f'update data provided: {supplied_update_info}')
            raise JiraProxyError(problem)
        return True


    def deleteIssue(self, issue_key):
        options = {'deleteSubtasks' :  True}
        status, result, errors = self.jira_comm.deleteRequest(f"issue/{issue_key}", **options)

        if errors:
            problem = f'Error deleting issue {issue_key} : {errors}'
            raise JiraProxyError(problem)

        return True


    ## TODO for the future: Add calls to query for workflow schemes and workflows. 
    ##      May do outside of JiraProxy.

    def getTransitions(self, issue_key):
        endpoint = f'issue/{issue_key}/transitions'
        status, result, errors = self.jira_comm.getRequest(endpoint)
        if errors:
            raise JiraProxyError(errors)

        transitions = {}

        for trans in result["transitions"]:
            transitions[trans["name"]] = {"action_id"      :  trans["id"],
                                          "end_state_name" :  trans["to"]["name"],
                                          "end_state_id"   :  trans["to"]["id"]}
        return transitions


    def transitionIssueState(self, issue_key, action_name, resolution=None):
        issue = self.getIssue(issue_key)
        issue.Status = action_name
        if resolution:
            issue.Resolution = resolution

        try:
            self.updateIssue(issue)
        except Exception as ex:
            problem = ex.args[0]
            # don't need to pass or re-raise this exception
        self.transitionIssueStateInNonDefaultWorkflow(issue_key, action_name, resolution)
        updated_issue = self.getIssue(issue_key)
        return updated_issue


    def transitionIssueStateInNonDefaultWorkflow(self, issue_key, action_name, resolution=None):
        fields = {}
        if resolution:
            fields = {"resolution" :  {"name" :  resolution}} 

        transitions = self.getTransitions(issue_key)

        if action_name not in transitions:
            end_state_match = [(action, info) for action, info in transitions.items()
                                               if info['end_state_name'] == action_name]
            if end_state_match:
                action_name, info = end_state_match[0] # there should only be 1 match resulting from above
            else:
                problem = f'Transition action |{action_name}| not valid for issue |{issue_key}|'
                raise JiraProxyError(problem)

        action_id = transitions[action_name]["action_id"]

        post_data = {"fields"     :  fields ,
                     "transition" :  {"id" :  action_id }
                    }

        status, result, errors = self.jira_comm.postRequest(f"issue/{issue_key}/transitions", post_data)
        if errors:
            raise JiraProxyError(errors)
       
        if status != 204:
            return None

        return self.getIssue(issue_key)


    def getFieldsForAction(self, issue_key, action_name):
        if action_name not in self.action_fields:
            self.action_fields[action_name] = []
            options = {"expand" :  "transitions.fields"}
            endpoint = f'issue/{issue_key}/transitions'
            status, info, errors = self.jira_comm.getRequest(endpoint, **options)
            if errors:
                raise JiraProxyError(errors)
            transition = [t for t in info["transitions"] if t["name"] == action_name]
            if not transition:
                  problem = (f'No transition named |{action_name}| allowed/found for '
                             f'issue |{issue_key}| with user |{self.jira_user}|')
                  raise JiraProxyError(problem)
            updatable_fields = transition["fields"]
            for jira_field_name, field_info in updatable_fields.items():
                display_name = field_info["name"]
                #if display_name == 'resolution': display_name = 'Resolution'
                self.action_fields[action_name] << [jira_field_name, display_name]

        return self.action_fields[action_name]


    def getComments(self, issue_key):
        endpoint = f'issue/{issue_key}/comment'
        status, result, errors = self.jira_comm.getRequest(endpoint)
        if errors:
            raise JiraProxyError(errors)
  
        return result["comments"]


    def addComment(self, issue_key, comment, visibility=None):
        # TODO: Is it possible to force the author of the comment to be someone other than
        #       the user specified in the Basic auth section of POST headers?
        comment_post = {"body" :  comment}
        # TODO: what about the visibility section?  it appears to be optional.
        #       for "type" :  "role", valid "value" targets are Administrators, Developers, Users
        #       can we put something in there other than the role type?
        default_visibility = {"type" :  "role", "value" :  "Users"}
        if visibility:
            comment_post["visibility"] = default_visibility
        else:
            comment_post["visibility"] = visibility
        endpoint = f'issue/{issue_key}/comment'
        status, result, errors = self.jira_comm.postRequest(endpoint, comment_post)
        if errors:
            raise JiraProxyError(errors)

        return True


    def getIssueAttachmentsInfo(self, issue_key):
        options = {"fields" :  "attachment"}
        endpoint = f'issue/{issue_key}'
        status, result, errors = self.jira_comm.getRequest(endpoint, **options)
        if errors:
            raise JiraProxyError(errors)
        atts = result["fields"]["attachment"]
        attachments = [JiraAttachmentMeta(att) for att in atts]
        return attachments


    def getAttachmentContent(self, att_info):
        status, attachment_content, errors = self.jira_comm.getAttachment(att_info)
        if errors:
            raise JiraProxyError(errors)
        return attachment_content


    def addAttachmentsToIssue(self, issue_key, attachments):
        # each item in attachments must be a dict with
        #  'filename', 'mimetype' and possibly 'base64content' keys
        # If a file exists for the filename value, then the content of that
        # file is used.
        # If a file does NOT exist for the 'filename' key, but there is a value
        # for the 'base64content' that can be decoded, then a temporary file
        # with the name of filename is written with the decoded content into
        # the current directory and provided to post_attachment, the temporary
        # file is removed prior to returning from this method
        endpoint = f'attachment/meta'
        status, info, errors = self.jira_comm.getRequest(endpoint)
        if not info["enabled"]:
            problem = "Uploading attachments not enabled"
            raise JiraProxyError(problem)
        size_limit = int(info["uploadLimit"])
        result = {}
        for att_info in attachments:
            # determine if att_info['filename'] exists
            # and if not, does att_info['base64content'] exist?
            # if it does, decode the base64content and  
            # write it into a file name named for att_info['filename']

            filename = att_info['filename']
            if att_info.get('file_content', False):
                att_info['file_content'] = str(att_info['file_content'])
            if att_info.get('base64content', False):
                att_info['file_content'] = base64.b64decode(att_info['base64content']).decode('UTF-8')
            result[filename] = {"added" : True, "error" : None}
            file_size = len(att_info['file_content'])
            if file_size > size_limit:
                err_msg = f"{filename} filesize of {file_size} too large for upload, skipped"
                result[filename] = {"added" :  False, "error" :  err_msg}
            else:
                status, info, errors = self.jira_comm.postAttachment(issue_key, att_info)
                if errors:
                    result[filename] = {"added" :  False, "error" :  errors}
        return result


    def getPermissions(self, project):
        project_key = self._getProjectKey(project)
        options = {'projectKey' :  project_key}
        if self.jira_comm.on_demand:
            options['permissions'] = (f'BROWSE_PROJECTS,CREATE_ISSUES,EDIT_ISSUES'
                                      f',SCHEDULE_ISSUES,ASSIGN_ISSUES,ASSIGNABLE_USER'
                                      f',RESOLVE_ISSUES,CLOSE_ISSUES,MODIFY_REPORTER'
                                      f',ADD_COMMENTS,CREATE_ATTACHMENTS,TRANSITION_ISSUES'
                                     )
        else:
            options['permissions'] = (f'BROWSE,CREATE_ISSUE,EDIT_ISSUE,SCHEDULE_ISSUE'
                                      f',ASSIGN_ISSUE,ASSIGNABLE_USER,RESOLVE_ISSUE'
                                      f',CLOSE_ISSUE,MODIFY_REPORTER,COMMENT_ISSUE,CREATE_ATTACHMENT'
                                     )
        endpoint = 'mypermissions'
        status, result, errors = self.jira_comm.getRequest(endpoint, **options)
        if errors:
            raise JiraProxyError(errors)

        if status != 200:
            raise JiraProxyError(f'REST call to mypermissions returned {status}')

        return result["permissions"]

    def _getProjectKey(self, project_identifier):
        proj_info = self.getProjects()
        if not proj_info or len(proj_info) == 0:
            raise JiraProxyError('No projects found in the JIRA instance')
        #result = proj_info.select{|key, value| key == project_identifier}
        result = [(key, value) for key, value in proj_info.items() if key == project_identifier]
        if result and len(result) != 0:
            return project_identifier
        #result = proj_info.select{|key, value| value == project_identifier}
        result = [(key, value) for key, value in proj_info.items() if value == project_identifier]
        if not result or len(result) == 0:
            raise JiraProxyError(f'Could not find project for identifier: {project_identifier}')
        project_key = result[0][0]
        return project_key

    def ensureMetaInformationSupport(self, project_key, issue_type):
        if project_key not in self.standard_fields:
            self._getFields(project_key, issue_type)
        if issue_type not in self.standard_fields[project_key]:
            self._getFields(project_key, issue_type)

        if "Summary" not in self.standard_fields[project_key][issue_type]:
            problem = (f'Error in jiraProxy.ensureMetaInformationSupport for '
                       f' project_key : {project_key}, issue_type: {issue_type} : '
                       f'Summary field does not exist.')
            raise JiraProxyError(problem)
        if 'edit' not in self.standard_fields[project_key][issue_type]["Summary"]:
            self._getFields(project_key, issue_type)
        # assert that self.standard_fields has project_key at first level, issue_type at second level


    def makeAnIssueInstance(self, jira_item):

        proj_key   = None
        issue_type = None

        if not jira_item:
            message = "In JiraProxy.makeAnIsueInstance: jira_item is None"
            self.logger.error(message)
            raise JiraProxyError(message)

        try:
            if 'key' not in jira_item:
                raise JiraProxyError("in makeAnIssueInstance, jira_item has no 'key' field")
            proj_key, iss_seq_num = jira_item["key"].split('-')

            self.logger.debug(f"Jira Issue Instance: {jira_item['key']}")
        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb = traceback.format_tb(exc_tb)
            context = f"while attempting to obtain key value: {key} in jira_item {repr(jira_item)}"
            problem = (f'Exception detected in JiraProxy.makeAnIssueInstance {context}: '
                       f'{exc_type.__name__}({exc_value}) exception')
            self.logger.error(problem)
            raise JiraProxyError("insufficent info to construct a JiraIssue instance")

        try:
            if "fields" not in jira_item:
                problem = "in makeAnIssueInstance, jira_item has no 'fields' field"
                raise JiraProxyError(problem)
            if "issuetype" not in jira_item['fields']:
                problem = "in makeAnIssueInstance, jira_item['fields'] has no 'issuetype' entry"
                raise JiraProxyError(problem)
            if "name" not in jira_item['fields']['issuetype']:
                problem = "in makeAnIssueInstance, jira_item['fields']['issuetype'] has no 'name' entry"
                raise JiraProxyError(problem)
            issue_type = jira_item["fields"]["issuetype"]["name"]
            self.logger.debug(f"issue_type: |{issue_type}|")
        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb = traceback.format_tb(exc_tb)
            context = f"while attempting to obtain issuetype info from jira_item {repr(jira_item)}"
            problem = (f'Exception detected in JiraProxy.makeAnIssueInstance {context}: '
                       f'{exc_type.__name__}({exc_value}) exception')
            self.logger.error(problem)
            brief = "Error getting a basic attribute from jira_item ('fields' or 'issuetype' or 'name')"
            raise JiraProxyError(brief)

        try:
            self.logger.debug(f"Calling ensureMetaInformationSupport for proj_key: {proj_key}, issue_type: {issue_type}")
            self.ensureMetaInformationSupport(proj_key, issue_type)
        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb = traceback.format_tb(exc_tb)
            brief = "Error calling ensureMetaInformationSupport"
            problem = (f'Exception detected in JiraProxy.makeAnIssueInstance {brief}: '
                       f'{exc_type.__name__}({exc_value}) exception')
            self.logger.error(problem)
            raise JiraProxyError(brief)

        try:
            self.logger.debug(f"Attempting to obtain a JiraIssue instance for {jira_item['key']}")
            jira_issue = JiraIssue(jira_item, self)
            self.logger.debug(f"Obtained JiraIssue for {jira_issue.key}")
            return jira_issue
        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb = traceback.format_tb(exc_tb)
            brief = "Error obtaining JiraIssue instance for jira_item data"
            problem = (f'Exception detected in JiraProxy.makeAnIssueInstance, {brief}: '
                       f'{exc_type.__name__}({exc_value}) exception')
            self.logger.error(problem)
            raise JiraProxyError(brief)

