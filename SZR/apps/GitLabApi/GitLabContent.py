def get_group(parent_id=None):
    group = {
        "id": 1,
        "name": "Foobar Group",
        "path": "foo-bar",
        "description": "An interesting group",
        "visibility": "public",
        "lfs_enabled": True,
        "avatar_url": "http://localhost:3000/uploads/group/avatar/1/foo.jpg",
        "web_url": "http://localhost:3000/groups/foo-bar",
        "request_access_enabled": False,
        "full_name": "Foobar Group",
        "full_path": "foo-bar",
        "file_template_project_id": 1,
        "parent_id": parent_id
    }
    return group


def get_group_list(size=6):
    group_list = []
    for idx in range(0, size):
        group = get_group()
        group['id'] = idx + 1
        group_list.append(group)
    return group_list


def get_new_group_args():
    group = get_group()
    new_group = {
        "name": group['name'],
        "path": group['path'],
        "description": group['description'],
        "visibility": group['visibility'],
        "lfs_enabled": group['lfs_enabled'],
        "request_access_enabled": group['request_access_enabled'],
        "parent_id": group['parent_id']
    }
    return new_group


def get_subgroup_list(size=6, parent_id=1):
    subgroup_list = get_group_list(size)
    for subgroup in subgroup_list:
        subgroup['parent_id'] = parent_id
    return subgroup_list


def get_group_project():
    project = {
        "id": 9,
        "description": "foo",
        "default_branch": "master",
        "tag_list": [],
        "archived": False,
        "visibility": "internal",
        "ssh_url_to_repo": "git@gitlab.example.com/html5-boilerplate.git",
        "http_url_to_repo": "http://gitlab.example.com/h5bp/html5-boilerplate.git",
        "web_url": "http://gitlab.example.com/h5bp/html5-boilerplate",
        "name": "Html5 Boilerplate",
        "name_with_namespace": "Experimental / Html5 Boilerplate",
        "path": "html5-boilerplate",
        "path_with_namespace": "h5bp/html5-boilerplate",
        "issues_enabled": True,
        "merge_requests_enabled": True,
        "wiki_enabled": True,
        "jobs_enabled": True,
        "snippets_enabled": True,
        "created_at": "2016-04-05T21:40:50.169Z",
        "last_activity_at": "2016-04-06T16:52:08.432Z",
        "shared_runners_enabled": True,
        "creator_id": 1,
        "namespace": {
            "id": 5,
            "name": "Experimental",
            "path": "h5bp",
            "kind": "group"
        },
        "avatar_url": None,
        "star_count": 1,
        "forks_count": 0,
        "open_issues_count": 3,
        "public_jobs": True,
        "shared_with_groups": [],
        "request_access_enabled": False
    }
    return project


def get_group_project_list(size=6, namespace_id=1):
    project_list = []
    for idx in range(0, size):
        project = get_group_project()
        project['id'] = idx + 1
        project['namespace']['id'] = namespace_id
        project_list.append(project)
    return project_list


def get_group_member():
    member = {
        "id": 1,
        "username": "raymond_smith",
        "name": "Raymond Smith",
        "state": "active",
        "avatar_url": "https://www.gravatar.com/avatar/c2525a7f58ae3776070e44c106c48e15?s=80&d=identicon",
        "web_url": "http://192.168.1.8:3000/root",
        "expires_at": "2012-10-22T14:13:35Z",
        "access_level": 30
    }
    return member


def get_group_member_list(size=6):
    member_list = []
    for idx in range(0, size):
        member = get_group_member()
        member['id'] = idx + 1
        member_list.append(member)
    return member_list


def get_group_member_all(size=6, list_size=6):
    member_all = get_group_member_list(list_size)
    for idx in range(list_size, list_size + size):
        member = get_group_member()
        member['id'] = idx + 1
        member_all.append(member)
    return member_all


def get_new_group_member_args(id=1):
    member = get_group_member()
    new_member = {
        "id": id,
        "user_id": member['id'],
        "access_level": member['access_level'],
        "expires_at": member['expires_at']
    }
    return new_member


def get_user():
    user = {
        "id": 1,
        "username": "john_smith",
        "name": "John Smith",
        "state": "active",
        "avatar_url": "http://localhost:3000/uploads/user/avatar/1/cd8.jpeg",
        "web_url": "http://localhost:3000/john_smith"
    }
    return user


def get_user_list(size=6):
    user_list = []
    for idx in range(0, size):
        user = get_user()
        user['id'] = idx + 1
        user_list.append(user)
    return user_list


def get_new_user_args():
    user = get_user()
    new_user = {
        "username": user['username'],
        "name": user['name'],
        "email": "email@example.com",
    }
    return new_user


def get_project():
    project = {
        "id": 3,
        "description": None,
        "default_branch": "master",
        "visibility": "private",
        "ssh_url_to_repo": "git@example.com:diaspora/diaspora-project-site.git",
        "http_url_to_repo": "http://example.com/diaspora/diaspora-project-site.git",
        "web_url": "http://example.com/diaspora/diaspora-project-site",
        "readme_url": "http://example.com/diaspora/diaspora-project-site/blob/master/README.md",
        "tag_list": [
            "example",
            "disapora project"
        ],
        "owner": {
            "id": 3,
            "name": "Diaspora",
            "created_at": "2013-09-30T13:46:02Z"
        },
        "name": "Diaspora Project Site",
        "name_with_namespace": "Diaspora / Diaspora Project Site",
        "path": "diaspora-project-site",
        "path_with_namespace": "diaspora/diaspora-project-site",
        "issues_enabled": True,
        "open_issues_count": 1,
        "merge_requests_enabled": True,
        "jobs_enabled": True,
        "wiki_enabled": True,
        "snippets_enabled": False,
        "resolve_outdated_diff_discussions": False,
        "container_registry_enabled": False,
        "created_at": "2013-09-30T13:46:02Z",
        "last_activity_at": "2013-09-30T13:46:02Z",
        "creator_id": 3,
        "namespace": {
            "id": 3,
            "name": "Diaspora",
            "path": "diaspora",
            "kind": "group",
            "full_path": "diaspora"
        },
        "import_status": "none",
        "import_error": None,
        "permissions": {
            "project_access": {
                "access_level": 10,
                "notification_level": 3
            },
            "group_access": {
                "access_level": 50,
                "notification_level": 3
            }
        },
        "archived": False,
        "avatar_url": "http://example.com/uploads/project/avatar/3/uploads/avatar.png",
        "license_url": "http://example.com/diaspora/diaspora-client/blob/master/LICENSE",
        "license": {
            "key": "lgpl-3.0",
            "name": "GNU Lesser General Public License v3.0",
            "nickname": "GNU LGPLv3",
            "html_url": "http://choosealicense.com/licenses/lgpl-3.0/",
            "source_url": "http://www.gnu.org/licenses/lgpl-3.0.txt"
        },
        "shared_runners_enabled": True,
        "forks_count": 0,
        "star_count": 0,
        "runners_token": "b8bc4a7a29eb76ea83cf79e4908c2b",
        "public_jobs": True,
        "shared_with_groups": [
            {
                "group_id": 4,
                "group_name": "Twitter",
                "group_full_path": "twitter",
                "group_access_level": 30
            },
            {
                "group_id": 3,
                "group_name": "Gitlab Org",
                "group_full_path": "gitlab-org",
                "group_access_level": 10
            }
        ],
        "repository_storage": "default",
        "only_allow_merge_if_pipeline_succeeds": False,
        "only_allow_merge_if_all_discussions_are_resolved": False,
        "printing_merge_requests_link_enabled": True,
        "request_access_enabled": False,
        "merge_method": "merge",
        "approvals_before_merge": 0,
        "statistics": {
            "commit_count": 37,
            "storage_size": 1038090,
            "repository_size": 1038090,
            "lfs_objects_size": 0,
            "job_artifacts_size": 0
        },
        "_links": {
            "self": "http://example.com/api/v4/projects",
            "issues": "http://example.com/api/v4/projects/1/issues",
            "merge_requests": "http://example.com/api/v4/projects/1/merge_requests",
            "repo_branches": "http://example.com/api/v4/projects/1/repository_branches",
            "labels": "http://example.com/api/v4/projects/1/labels",
            "events": "http://example.com/api/v4/projects/1/events",
            "members": "http://example.com/api/v4/projects/1/members"
        }
    }
    return project


def get_project_list(size=6):
    project_list = []
    for idx in range(0, size):
        project = get_project()
        project['id'] = idx + 1
        project_list.append(project)
    return project_list


def get_new_project_args():
    project = get_project()
    new_project = {
        "path": project['path'],
        "name": project['name'],
    }
    return new_project


def get_project_member():
    member = {
        "id": 1,
        "username": "raymond_smith",
        "name": "Raymond Smith",
        "state": "active",
        "avatar_url": "https://www.gravatar.com/avatar/c2525a7f58ae3776070e44c106c48e15?s=80&d=identicon",
        "web_url": "http://192.168.1.8:3000/root",
        "expires_at": "2012-10-22T14:13:35Z",
        "access_level": 30
    }
    return member


def get_project_member_list(size=6):
    member_list = []
    for idx in range(0, size):
        member = get_project_member()
        member['id'] = idx + 1
        member_list.append(member)
    return member_list


def get_project_member_all(size=6, list_size=6):
    member_all = get_project_member_list(list_size)
    for idx in range(list_size, list_size + size):
        member = get_project_member()
        member['id'] = idx + 1
        member_all.append(member)
    return member_all


def get_new_project_member_args(id=1):
    member = get_project_member()
    new_member = {
        "id": id,
        "user_id": member['id'],
        "access_level": member['access_level'],
        "expires_at": member['expires_at']
    }
    return new_member
