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


def get_project():
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


def get_project_list(size=6, namespace_id=1):
    project_list = []
    for idx in range(0, size):
        project = get_project()
        project['id'] = idx + 1
        project['namespace']['id'] = namespace_id
        project_list.append(project)
    return project_list


def get_member():
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


def get_member_list(size=6):
    member_list = []
    for idx in range(0, size):
        member = get_member()
        member['id'] = idx + 1
        member_list.append(member)
    return member_list


def get_member_all(size=6, list_size=6):
    member_all = get_member_list(list_size)
    for idx in range(list_size, list_size + size):
        member = get_member()
        member['id'] = idx + 1
        member_all.append(member)
    return member_all


def get_new_member_args(id=1):
    member = get_member()
    new_member = {
        "id": id,
        "user_id": member['id'],
        "access_level": member['access_level'],
        "expires_at": member['expires_at']
    }
    return new_member
