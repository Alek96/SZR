from django.test import TestCase

from groups.forms import VisibilityLevelForm, GroupForm


class AbstractVisibilityLevelTest(TestCase):
    def test_init(self):
        VisibilityLevelForm()


class GroupFormTests(TestCase):
    def test_init(self):
        GroupForm()

    def test_valid_data(self):
        form_data = {
            'name': "Group_name",
            'path': "Group_path",
            'description': "Description",
            'visibility': "private",
        }
        form = GroupForm(form_data)
        self.assertTrue(form.is_valid())
        for key, value in form_data.items():
            self.assertEqual(form.cleaned_data[key], value)

    def test_blank_data(self):
        form = GroupForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], ['This field is required.'])
        self.assertEqual(form.errors['path'], ['This field is required.'])
