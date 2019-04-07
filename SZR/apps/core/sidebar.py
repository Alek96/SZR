class Sidebar:
    def __init__(self, title, name, search=False, **kwargs):
        self.title = title
        self.name = name
        self.search = search
        self.points = []


class Point:
    def __init__(self, name, url=None, icon='', badge='', sub_points=None, active=False, **kwargs):
        self.name = name
        self.url = url or Url()
        self.icon = icon
        self.badge = badge
        self.sub_points = sub_points if sub_points else []
        self.active = active

    def __str__(self):
        return '<a {}> {} <span>{}</span> {} </a>'.format(self.url, self.icon, self.name, self.badge)


class Url:
    def __init__(self, url='#', **kwargs):
        self.url = url
        self.extras = ''

    def __str__(self):
        return 'href={0} {1}'.format(self.url, self.extras)


class NewPageUrl(Url):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extras = 'target=_blank rel="noopener noreferrer"'


class Icon:
    def __init__(self, **kwargs):
        self.code = ''

    def __str__(self):
        return '<i class="fa {0}"></i>'.format(self.code)


class HomeIcon(Icon):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = 'fa-home'


class UsersIcon(Icon):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = 'fa-users'


class TasksIcon(Icon):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = 'fa-tasks'


class SettingIcon(Icon):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = 'fa-cog'


class Badge:
    def __init__(self, text, **kwargs):
        self.text = text
        self.code = ''

    def __str__(self):
        return '<span class="badge badge-pill {0}">{1}</span>'.format(self.code, self.text)


class SuccessBadge(Badge):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = 'badge-success'


class WarningBadge(Badge):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code = 'badge-warning'
