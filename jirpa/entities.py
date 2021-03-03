# Copyright 2021 Broadcom, Inc.   All Rights Reserved.

class JiraServerInfo:

    def __init__(self, info):
        self.url          = info["baseUrl"]
        self.version      = info["version"]
        self.server_title = info["serverTitle"]
        self.server_time  = info["serverTime"]

#######################################################################################

class JiraUser:

    def __init__(self, info):
        self.name    = info["name"]
        self.email   = info["emailAddress"]
        self.active  = info["active"]
        self.display_name = info["displayName"]
        self._info = info

    def info(self):
        detail = (f"name: {self.name:<10}  display name: {self.display_name:<18}  "  
                  f"active? {self.active:<5}  email: {self.email}")
        return detail

#######################################################################################

class JiraAttachmentMeta:

    def __init__(self, attach_info):
        self.filename    = attach_info["filename"]
        self.created     = attach_info["created"] # was Time.parse for this construct...
        self.filesize    = int(attach_info["size"])
        self.mimetype    = attach_info["mimeType"]
        self.content_ref = attach_info["content"]
        self.author      = attach_info.get("author", None)
        if self.author:
            authname = attach_info["author"].get("name", None)
            if authname:
                self.author = authname

#######################################################################################

class JiraFieldSchema:
    """
        Given information for a specific field
        populate attributes that provide specific info like name, display_name,
        is_custom_field?, is_standard_field?, structure, data_type
    
        returned by jira_proxy.fieldSchema("project","issue_type", "field_name")
    """

    def __init__(self, field_info, standard, custom):
        if 'create' in field_info:
            info = field_info['create']
        else:
          info = field_info['edit']
        if standard:
             self.name  = info['schema']['system']
        else:
            self.name   = "customfield_" + str(info['schema']['customId'])
        self.display_name = info['name']
        self.standard     = standard
        self.custom       = custom
        self.structure    = 'atom'
        self.data_type    = info['schema']['type']
        self.allowed_values = None
        if 'allowedValues' in info:
            self.allowed_values = [av['name'] for av in info['allowedValues']]

        if isinstance(info['schema']['type'], list):
            self.structure = 'array'
            self.data_type = info['schema']['items']

    def is_standard_field(self):
        return self.standard

    def is_custom_field(self):
        return self.custom

