# jirpa : Python based package supporting basic Jira operations via REST API

Changes listed at the bottom of this document.


## Dependencies

requirements.txt

## Development Environment 

Python 3.8.x
Python 3.7.x
Python 3.6.x

pip install -r requirements.txt

## Packaging for use

setup.py, setup.cfg

build_dist.py

## Installation

Obtain and unarchive the package distribution 
  If you unpack this in /home/targo, you'll see a jirpa subdirectory
    with __init__.py
         jiracomm.py
         jiraproxy.py
         entities.py
         jiraissue.py
set your PYTHONPATH to include the directory where you unpacked this
  (as in the example above, export PYTHONPATH=/home/targo


## pytest tests
For your cloned working repository, there is a test subdirectory with 
tests written using pytest (see link for pytest).
These tests assume a working Jira Server instance with some 
specific configurations made to it.
Those configurations are 
described in the [Jira-Setup.md](Jira-Setup.md) file.  Those configurations
also involve updating the [jira_targets.py](test/jira_targets.py) in the test directory.


Once Jira and the test/jira_targets.py file have been setup, to run the pytest suite, 
situate in the base directory for your working repo:

    pytest test/test_*.py
    
## Example Code

The directory examples contains sample Python scripts that use the jirpa package.
If you run them from the base directory, you don't need to change your PYTHONPATH
content (from the setting described above).  If you situate in the examples subdirectory
you'll need to adjust or add to your PYTHONPATH content (ie., /home/targo/jirpa).

### 01_show_version.py
This script just prints to standard out the version of the rally_jest gem.

### 02_jira_proxy.py
Example showing a set of configurations used to create a jira_proxy (ie, a JiraProxy instance). 
Only one of the configurations will work, the others will raise exceptions. The 
purpose of the failing configurations is to show what kind of exceptions are
raise and what the error messages will look like.

### 03_jira_info.py
Display the server info.

### 04_list_projects.py
Show the use of both JiraProxy.getProjects() and JiraProxy.getProjectsDetails() .
The getProjects returns a dict where the key is the project key and the value is
project name.  GetProjectsDetails returns an Array where each element is a dict.
The dict has these keys: Key, Name, Description and Details.  The Details value
is the actual result of the project/<project_key> REST call as a dict.

### 05_list_issues.py
This example list all of the issues returned using a JQL search statement.  In this
case the first JQL will return all issues belonging to the JEST project. The second
JQL will return just the story issues for the JEST project. The second JQL request that
the issues be ordered by their keys.

### 06_show_display_names.py
Issue attributes within Jira are reference by their Display Name or their attribute
key.  The Display Name is the string displayed in the web page interfaces. The attribute
key is the string used in REST api.  (Also, attribute keys are used in the source
code of Jira itself.)  For example the summary of an issue has the Display Name of
"Summary" and the attribute key of "summary".  Custom field attribute keys are not
named as nicely.  Take for example the Rally ID field:
The Display name is "RallyID" and the attribute key is customfield_10103.
The number portion of the attribute key for a custom field will likely differ 
between Jira instances.
Note that the Display Names can contain spaces.

Issue attributes can be modified by setting new values using their Display Names as
either methods to the issue object or as Dict keys to those objects.  For example both
of these lines are valid ways to set Summary:
```python
   issue.Summary    = "Bad Bug"
   issue["Summary"] = "Bad Bug"
```
Example 06 lists of the Display Names of attributes whose values can be read and written to.

### 07_create_issue.py
Creating an issue starts by creating a dict using the attribute Display Names as
keys pointing to values needed at an issue's creation.  Pass that dict along with
a Project Key and issue type to JiraProxy.createIssue to create an issue.

An issue has many useful "Read Only" values beyond the values listed by example 06.  Besides
creating an issue example 07 will then retrieve the new issue and list both the Read Only and
Settable values of the issue. Note that the read only values do not have Display Names and
use instead their attribute keys for accessing their values.  These lines show how the created
value can be accessed:
```python
   create_date = issue.created
   create_date = issue["created"]
```

### 08_updata_issue.py
Example 08 shows how to update an issue.  The scripts follows these steps:
 1. Values for the issue at creation are set.
 1. Issue is created.
 1. Issue Retrieved and values printed out.
 1. The Description value is updated
 1. The issue object is sent back to jira for updating.
 1. Retrieved again and the updated values are printed out.


## Change Log

### Version 1.0.0
Initial conversion from Ruby based rally-jest gem.



