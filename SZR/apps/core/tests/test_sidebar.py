import unittest

from core import sidebar


class SidebarTests(unittest.TestCase):
    def test_init_default(self):
        bar = sidebar.Sidebar(title='title', name='name')
        self.assertEqual(bar.title, 'title')
        self.assertEqual(bar.name, 'name')
        self.assertEqual(bar.search, False)
        self.assertEqual(bar.points, [])

    def test_init(self):
        bar = sidebar.Sidebar(title='title', name='name', search=True)
        self.assertEqual(bar.search, True)


class PointTests(unittest.TestCase):
    def test_init_default(self):
        point = sidebar.Point(name='name')
        self.assertEqual(point.name, 'name')
        self.assertEqual(point.url.url, '#')
        self.assertEqual(point.icon, '')
        self.assertEqual(point.badge, '')
        self.assertEqual(point.sub_points, [])
        self.assertEqual(point.active, False)

    def test_init(self):
        url = sidebar.Url()
        icon = sidebar.Icon()
        badge = sidebar.Badge(text='badge')
        sub_points = ['points']
        active = True

        point = sidebar.Point(name='name', url=url, icon=icon, badge=badge, sub_points=sub_points, active=active)
        self.assertEqual(point.url, url)
        self.assertEqual(point.icon, icon)
        self.assertEqual(point.badge, badge)
        self.assertEqual(point.sub_points, sub_points)
        self.assertEqual(point.active, active)

    def test_string_representation(self):
        point = sidebar.Point(name='name')
        point.url = 'abc'
        point.icon = 'def'
        point.badge = 'ghi'
        self.assertEqual(str(point),
                         '<a {}> {} <span>{}</span> {} </a>'.format(point.url, point.icon, point.name, point.badge))


class UrlTests(unittest.TestCase):
    def test_init_default(self):
        url = sidebar.Url()
        self.assertEqual(url.url, '#')
        self.assertEqual(url.extras, '')

    def test_init(self):
        url = sidebar.Url(url='name')
        self.assertEqual(url.url, 'name')

    def test_string_representation(self):
        url = sidebar.Url(url='name')
        url.extras = 'abc'
        self.assertEqual(str(url), 'href={0} {1}'.format(url.url, url.extras))


class NewPageUrlTests(unittest.TestCase):
    def test_init_default(self):
        url = sidebar.NewPageUrl()
        self.assertEqual(url.url, '#')
        self.assertEqual(url.extras, 'target=_blank rel="noopener noreferrer"')

    def test_init(self):
        url = sidebar.NewPageUrl(url='name')
        self.assertEqual(url.url, 'name')


class IconTests(unittest.TestCase):
    def test_init(self):
        icon = sidebar.Icon()
        self.assertEqual(icon.code, '')

    def test_string_representation(self):
        icon = sidebar.Icon()
        icon.code = 'abc'
        self.assertEqual(str(icon), '<i class="fa {0}"></i>'.format(icon.code))


class HomeIconTests(unittest.TestCase):
    def test_init(self):
        icon = sidebar.HomeIcon()
        self.assertEqual(icon.code, 'fa-home')


class UsersIconTests(unittest.TestCase):
    def test_init(self):
        icon = sidebar.UsersIcon()
        self.assertEqual(icon.code, 'fa-users')


class TasksIconTests(unittest.TestCase):
    def test_init(self):
        icon = sidebar.TasksIcon()
        self.assertEqual(icon.code, 'fa-tasks')


class SettingIconTests(unittest.TestCase):
    def test_init(self):
        icon = sidebar.SettingIcon()
        self.assertEqual(icon.code, 'fa-cog')


class BadgeTests(unittest.TestCase):
    def test_init(self):
        badge = sidebar.Badge(text='text')
        self.assertEqual(badge.text, 'text')
        self.assertEqual(badge.code, '')

    def test_string_representation(self):
        badge = sidebar.Badge(text='text')
        badge.code = 'abc'
        self.assertEqual(str(badge), '<span class="badge badge-pill {0}">{1}</span>'.format(badge.code, badge.text))


class SuccessBadgeTests(unittest.TestCase):
    def test_init(self):
        badge = sidebar.SuccessBadge(text='text')
        self.assertEqual(badge.code, 'badge-success')


class WarningBadgeTests(unittest.TestCase):
    def test_init(self):
        badge = sidebar.WarningBadge(text='text')
        self.assertEqual(badge.code, 'badge-warning')
