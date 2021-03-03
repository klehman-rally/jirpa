#jiraissue file for jirpa package

import re
import copy

###################################################################################################

CUSTOM_FIELD_PREFIX_PATTERN = re.compile(r'^customfield_(.*)')
ISO_8601_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3}Z?)?$')

class JiraIssueError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = "Dunno how to get any string arg yet..."

class JiraIssueFieldError(Exception): pass

###################################################################################################

class JiraIssue:
    protected_attributes = ['id', 'version', 'key', 'project_key', 'issue_type', 
                            'issue_type_id', 'logger',
                            'standard_fields', 'standard_field_names', 
                            'custom_fields',   'custom_field_names',
                            'std_display_for_sys', 'priority_value_for_id',
                            'special', 'updated_keys']

    def __init__(self, jira_item, jira_proxy):
        self.attribute    = {}
        self.updated_keys = []
        self.version                = jira_proxy.jira_version.version
        self.id                     = jira_item.get("id", 0)
        self.key                    = jira_item["key"]
        self.project_key            = self.key.split('-')[0]
        self.issue_type             = jira_item["fields"]["issuetype"]["name"]
        self.issue_type_id          = jira_proxy.issue_type_id_for_name[self.issue_type]
        self.logger                 = jira_proxy.logger

        self.standard_fields        = jira_proxy.standard_fields[self.project_key][self.issue_type]
        self.custom_fields          = jira_proxy.custom_fields[  self.project_key][self.issue_type]
        self.standard_field_names   = self.standard_fields.keys()
        self.custom_field_names     = self.custom_fields.keys()
        self.std_display_for_sys    = {}
        for display_name, tub in self.standard_fields.items():
            operation = 'create' if 'create' in tub else 'edit'
            sys_name = tub[operation]['schema']['system']
            self.std_display_for_sys[sys_name] = display_name
        self.priority_value_for_id  = jira_proxy.priority_value_for_id

        self.special = {'status'      : 'Status', 
                        'resolution'  : 'Resolution', 
                        'created'     : 'Created', 
                        'updated'     : 'Updated', 
                       }

##        print("--\nin JiraIssue ...") 
##        print(f'here is the incoming jira_item data:\n{repr(jira_item)}')
##        print('here are all the standard fields for the target issue type:')
##        for field_name, meta_info in self.standard_fields.items():
##                print(f"    {field_name}    {meta_info}")
        
        ##sfns = "\n    ".join(self.standard_field_names)
        ##print(f"here are the standard_field_names...\n    {sfns}")  # as Display Name 
        #jif_keys = "\n    ".join(jira_item["fields"].keys())
        #print(f'jira_item["fields"] has these keys: {jif_keys}')
        #print(f"jira_item['fields'] value is: {jira_item['fields']}")

        #extract the standard fields, within the jira_item['fields'] the fields are "system" names
        std_fields = {attr_name:value for attr_name, value in jira_item["fields"].items()
                                       if attr_name in self.std_display_for_sys
                                       or attr_name in self.standard_fields
                     }
##
##        sfns = "\n    ".join(list(std_fields.keys()))
##        print(f"here are the std_fields that are in the jira_item...\n    {sfns}")
##

        #extract the special fields
        special_fields = {attr_name:value for attr_name, value in jira_item["fields"].items()
                           if attr_name in self.special}

        #extract the custom  fields
        digit_suffix_custom_fields = {attr_name:value for attr_name, value in jira_item["fields"].items()
                                       if CUSTOM_FIELD_PREFIX_PATTERN.match(attr_name)}
       
        #extract other custom fields with names
        other_custom_fields = {attr_name:value for attr_name, value in jira_item["fields"].items()
                                if attr_name     in self.custom_field_names
                               and attr_name not in digit_suffix_custom_fields}

        # identify fields supplied that are not in a known classification
        unrecognized_fields = {attr_name:value for attr_name, value in jira_item["fields"].items()
                                                if attr_name not in self.standard_field_names
                                               and attr_name not in self.std_display_for_sys
                                               and attr_name not in self.custom_field_names
                                               and attr_name not in special_fields
                                               and attr_name not in digit_suffix_custom_fields
                                               and attr_name not in other_custom_fields}

        #if unrecognized_fields:
        #    raise JiraIssueError("Unrecognized fields: " + repr(unrecognized_fields))

        #process the bowls of different classification of field types

        # first process the standard fields
        for attr_name, value in std_fields.items():
##            print(f"std_field attr_name: |{attr_name}|")
            display_name = None
            for field_name, meta_info in self.standard_fields.items():
                if field_name == attr_name:
                    display_name = field_name
                    break
                elif 'create' in meta_info and str(meta_info['create']['schema']['system']) == attr_name:
                    # for reporter
                    display_name = field_name
                    break
                elif 'edit'   in meta_info and str(meta_info['edit'  ]['schema']['system']) == attr_name:
                    # for reporter
                    display_name = field_name
                    break

            end_value = self.parseAttributeValue(value)
            if display_name:
                self.attribute[display_name] = end_value
              ##  print(f"attr_name: {attr_name:<16}   display_name: {display_name:<16}  end_value: {end_value}")
            else:
                self.attribute[attr_name]    = end_value
              ##  print(f"attr_name: {attr_name:<16}   display_name: {'NO DISPLAY NAME':<16}  end_value: {end_value}")

        # next process the special fields
        for attr_name, value in special_fields.items():
            display_name = self.special[attr_name]
            self.attribute[display_name] = self.parseAttributeValue(value)

        # next do the "other" custom fields (easy...)
        for attr_name, value in other_custom_fields.items():
            self.attribute[attr_name] = self.parseAttributeValue(value)

        # now do the somewhat more complex digit-suffixed custom fields
        for attr_name, value in digit_suffix_custom_fields.items():
            cf_id = attr_name.replace('customfield_', '')
            custom_name = None
            for display_name, meta_info in self.custom_fields.items():

                if 'create' in meta_info:
                    if  str(meta_info['create']['schema']['customId']) == cf_id:
                      custom_name = display_name
                elif 'edit' in meta_info:
                    if  str(meta_info[  'edit']['schema']['customId']) == cf_id:
                        custom_name = display_name

            if not custom_name:
                ##TODO: Add logger to JiraIssue
                #logger.debug("JiraIssue.new: No meta data for #{attr_name}; possible obsolete custom field. ")
                pass
            else:
                ##TODO Check custom field value is a hash (much like for treatment below on standard fields)

                # Hack for DE17528
                if custom_name == "Sprint":
                    if value is not None:
                      #value.last =~ /id=(\d+)/
                      #@attribute["Sprint"] = $1
                      junk, value = value.split('id=', 1)
                      self.attribute["Sprint"] = value
                else:
                    self.attribute[custom_name] = self.parseAttributeValue(value)

        # now do the unrecognized fields (which may get flagged on an attempt to create this Jira)
        for attr_name, value in unrecognized_fields.items():
            self.attribute[attr_name] = self.parseAttributeValue(value)


##      print(f'here is JiraIssue instance attribute data:\n{repr(self.attribute)}')


    def parseAttributeValue(self, value):
        """
            TODO: Handle parsing of Multilevel selection/pickers field types ...?
        """
        parsed_value = value
        if isinstance(value, dict):
            if "name" in value:
                parsed_value = value["name"]
            elif "value" in value:
                parsed_value = value["value"]
        elif isinstance(value, list):
            if not value:
                parsed_value = None
            else:
                if isinstance(value[0], dict):
                    if "name" in value[0]:
                        parsed_value = [entry["name"]  for entry in value]
                    elif "value" in value[0]:
                        parsed_value = [entry["value"] for entry in value]
                else:
                    parsed_value = ",".join(value)

        return parsed_value


    # something to approximate method_missing for issue.x access for get
    def __getattr__(self, name):
        if name in self.attribute.keys():
            return self.attribute.get(name)
        return None

    # something to approximate method_missing for issue.x access for set
    def __setattr__(self, name, value):
        if name == 'attribute':
            super().__setattr__('attribute', value)
        elif name in JiraIssue.protected_attributes:
            super().__setattr__(name, value)
        else:
            self.__dict__['attribute'][name] = value
            self.markUpdated(name)

    def __getitem__(self, name):
        if name in self.__dict__.keys():
            return self.__dict__.get(name, None)
        elif name in self.__dict__['attribute']:
            return self.__dict__['attribute'].get(name, None)
        else:
            raise JiraIssueError(f'JiraIssue no attribute for: {name}')
        #print("--")
        #print(f"JiraIssue.__getitem__ called with arg of {name}")
        #print(repr(list(self.__dict__.keys())))
        #print("attribute keys:")
        #print(repr(self.__dict__['attribute'].keys()))
        #print("standard_field_names:")
        #print(f"{repr(self.__dict__['standard_field_names'])}")
        #print("custom_field_names:")
        #print(f"{repr(self.__dict__['custom_field_names'])}")
        #return self.__dict__.get(name, None)

    def __setitem__(self, key, value):
        if key != 'attribute' and key not in JiraIssue.protected_attributes and not isinstance(key, int):
            assign = False
            if key in self.std_display_for_sys.keys():
                assign = True
            if key in self.std_display_for_sys.values():
                assign = True
            # the above takes care of situation where key is 
            # either a display name or system name for a std field
            # have to take care of scenario where key is either display name or system name
            # for a custom field
            if key.startswith('customfield_'):
                assign = True
            if key in self.custom_field_names and 'edit' in self.custom_fields[key]:
                assign = True
            if assign:
                self.__dict__['attribute'][key] = value
                self.markUpdated(key)

    def markUpdated(self, key):
        if key not in self.updated_keys:
            self.updated_keys.append(key)

    def jiralize(self, mode):
        """
            This method has to structure a dict to match JIRA REST API expectations
              needs to know about:
                fields to handle differently in the resulting data structure (key, project)
                fields to skip (status, resolution)
                standard and custom fields
                special field name to id mappings
                shaping data value types accord to attribute name / type
        """
        post_data = {"fields" : {} }
        post_data["fields"]["project"]   = {"key" : self.project_key} 
        post_data["fields"]["issuetype"] = {"id"  : self.issue_type_id}

        jira_keys = self.attribute.keys() if mode == 'create' else self.updated_keys
        #jira_keys = self.attribute.keys() if mode == 'create' else self._updatedFields()


        for field_key in jira_keys:
            value = self.attribute[field_key]
            self.logger.debug(f"jiralize field_key: |{field_key}| has a value of |{value}|")
            ## TODO Do key, project, status and resolution have display names ?
            ## TODO Need to Handle multilevel selection/pickers field types.
            # skip things that are already set or can't be set by user
            if field_key in ['key', 'Project', 'Status', 'Created', 'Updated']:
                continue
            if field_key == 'Issue Type':
                # it is possible to transition a Jira issue to a different issue type
                post_data["fields"]["issuetype"] = {"name" : value}
                self.logger.debug(f"   setting post_data['fields']['issuetype'] to {value}")
                continue

            self.logger.debug(f"   checking to see if field_type of |{field_key}| "
                              f" is standard, custom or unrecognized")
            field_type   = ""
            std_field    = False
            custom_field = False

            if field_key in self.custom_fields and mode in self.custom_fields[field_key]:
                field_info = self.custom_fields[field_key][mode]
                field_type = field_info["schema"]["type"]
                # <HACK rallyid=DE17528>
                if field_info['schema']['custom'] == 'com.pyxis.greenhopper.jira:gh-sprint':
                    field_type = 'sprint'
                # </HACK>
                id = field_info["schema"]["customId"]
                field_key = f"customfield_{id}"
                custom_field = True
            elif field_key in self.standard_fields and mode in self.standard_fields[field_key]:
                field_info = self.standard_fields[field_key][mode]
                field_type = field_info["schema"]["type"]
                if field_key.startswith('Affects Version/s'):
                    field_type = 'versions'
                if field_key.startswith('Fix Version/s'):
                    field_type = 'versions'
                if field_key.startswith('Component/s'):
                    field_type = 'components'
                field_key = field_info["schema"]["system"]
                std_field = True
            elif field_key == 'issuetype':
                self.logger.debug("JiraIssue instance detected a field name of 'issuetype', this field is ignored")
                continue
            else:
                problem = (f"Unrecognized field |{field_key}|, unable to accurately realize "
                           f"postable data for this field in |{mode}| mode")
                raise JiraIssueError(problem)

            if "allowedValues" in field_info:
                allowed_values = self._allowedValuesForField(field_type, field_info, std_field)
                if not self._isAllowableValue(value, allowed_values):
                    problem =  (f'"{value}" not an allowed value for the {field_info["name"]} field,'
                                f' the allowed values for {field_key} are {repr(allowed_values)}')
                    raise JiraIssueError(problem)


                if custom_field and not re.search(r'versions?', field_type):
                    field_type = "select"  
                if custom_field and re.search(r'.*multiselect$', field_info["schema"]["custom"]):
                    field_type = "multiselect" 

            postable_value = self._postableValue(field_key, field_type, value)
            post_data["fields"][field_key] = postable_value

        return post_data

    def attributeNames(self):
        return list(self.attribute.keys())

    attributes = attributeNames


    def attributeValues(self):
        return [(key, value) for key, value in self.attribute.items()]

    # leftover TODO: return a dict of offical JIRA key name to JIRA Display name for each JIRA field

    def attributeDisplayNames(self):
        """
            Return a list of JIRA issue field DisplayNames
        """
        attr_names = []
        for mode in ['create', 'edit']:
            std_fld_names_for_mode =  [std_field_name 
                                         for std_field_name, std_field_info  
                                          in self.standard_fields.items()
                                          if mode in std_field_info
                                      ]
            attr_names.extend(std_fld_names_for_mode)

            custom_fld_names_for_mode = [custom_field_name 
                                           for custom_field_name, custom_field_info
                                            in self.custom_fields.items()
                                            if mode in custom_field_info
                                        ]
            attr_names.extend(custom_fld_names_for_mode)

        return list(set(attr_names)) # uniquify the attribute names


    def _allowedValuesForField(self, field_type, field_info, std_field):
        """
        """
        if std_field:
            allowed_values = [av["name"] for av in field_info["allowedValues"]]
        else:  # must be a custom field
            if re.search(r'versions?', field_type):  # version or versions
                allowed_values = [av["name"] for av in field_info["allowedValues"]]
            else:
                allowed_values = [av["value"] for av in field_info["allowedValues"]]

        return allowed_values


    def _isAllowableValue(self, value, allowed_values): 
        if isinstance(value, str):
            if not re.search(r', ?', value): # value String is NOT a sequence of comma separated values
                return (value in allowed_values)
            else:
                values = re.split(r', ?', value)  # either comma or comma-space between items
                valids = [val for val in values if val in allowed_values]
                return len(valids) == len(values)
        elif isinstance(value, list):
            valids = [val for val in values if val in allowed_values]
        else:
            return False


    def _postableValue(self, field_key, field_type, value):
        assignment = \
            {
             "string"       : (lambda x: x),
             "number"       : (lambda x: float(x)),
             "array"        : (lambda x: [item.strip() for item in x.split(',')]),
             "sprint"       : (lambda x: x),
             "user"         : (lambda x: {"name"  : x}),
             "resolution"   : (lambda x: {"name"  : x}),
             "version"      : (lambda x: {"name"  : x}),
             "priority"     : (lambda x: {"name"  : x}),
             "select"       : (lambda x: {"value" : x}),
             "multiselect"  : (lambda x: [{"value" : item.strip()} for item in x.split(",")]),
             "timetracking" : (lambda x: x),
             "date"         : (lambda x: str(x)),
            #"datetime"     : (lambda x: x), # this field_type gets some special checking/transformation
            }
        if field_type == 'datetime':
            if not ISO_8601_PATTERN.match(str(value)):
                problem = f"Postable value error: {field_type} {value} is not in a standard format"
                raise JiraIssueFieldError(problem)
            date_time, *junk = str(value).split('.', 1)
            postable_value = f"{date_time}.000-0000"
        elif field_type in ['versions', 'components']:
            postable_value = multipleValuesPossible(field_type, value)
        elif field_type in assignment:
            postable_value = assignment[field_type](value)
        else:
            problem = (f"JiraIssue.jiralize missing logic to set {field_key} "
                       f"value (of field_type |{field_type}|) with  value = |{value}|" )
            raise JiraIssueFieldError(problem)

        return postable_value

    def brief(self):
        """
            convenience method to blurt out interesting attribute : value info in an issue
        """
        tank = []
        tank.append(f'{"id":<16} : {self.id}')
        tank.append(f'{"key":<16} : {self.key}')
        if not self.attribute:  # it is empty
            return "\n".join(tank)
        if self.issue_type:
            tank.append(f'{"issue_type":<16} : {self.issue_type_id} {self.issue_type}')

        common = ['Summary', 'Description', 'Reporter', 'Assignee', 'Created', 'Updated', 'Priority', 'Status']
        for attr_name in common:
            attr_value = self.attribute.get(attr_name, False)
            if attr_value:
                tank.append(f'{attr_name:<16} : {repr(attr_value)}')
        if self.attribute.get('Resolution'):
            # check for None and not show that as a value?
            tank.append(f'{"Resolution":<16} : {self.attribute.get("Resolution")}')

        afvs = self.attribute.get('Affects Version/s', None)
        if afvs and len(afvs) > 0:
            if isinstance(afvs, dict):
                affvers = ",".join([afv["name"] for afv in afvs])
            else:
                affvers = afvs
            tank.append(f'{"Affects Version/s":<16} : {affvers}')

        fxvs = self.attribute.get('Fix Version/s',     None)
        if fxvs and len(fxvs) > 0:
            if isinstance(fxvs, dict):
                fixvers = ",".join([fxv["name"] for fxv in fxvs])
            else:
                fixvers = fxvs
            tank.append(f'{"Fix Version/s":<16} : {fixvers}')

        for jira_field_name in sorted(self.custom_fields.keys()):
           cf = self.custom_fields[jira_field_name]["create"]
           cf_id = f"customfield_{cf['schema']['customId']}"
           if jira_field_name in self.attribute:
             # see if the value is a Dict and if so, extract id and (name or value)
             value = self.attribute.get(jira_field_name, '')
             if isinstance(value, dict):
                 if "id" in value:
                     id_part = f"id --> {value['id']}"
                     if "name" in value:
                         target = f"name --> {value['name']}"
                     elif "value" in value:
                         target = f"value --> {value['value']}"
                     else:
                        target = str(value)
                     value = f"{id_part} {target}"
             if value:
                tank.append(f'{jira_field_name:<16} : {value:<15}  {cf_id}')

        tank = ["    " + item for item in tank] # prefix with 4 spaces 
        return "\n".join(tank)        


def multipleValuesPossible(field_type, value):
    if isinstance(value, str):
        postable_value = [{"name" : value}]
        if re.search(r', ?', value) is not None:  # comma separated like a,b,c or a, b, c ?
            postable_value = [{"name" : item} for item in re.split(r', ?', value)]
    elif isinstance(value, list):
        postable_value = [{"name" : item} for item in value]
    else:
        problem = f"Postable value error: {field_type} {value} is not a String or a List "
        raise JiraIssueFieldError(problem)

    return postable_value

