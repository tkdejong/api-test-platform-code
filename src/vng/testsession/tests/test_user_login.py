from django_webtest import WebTest
from django.urls import reverse
from factory.django import DjangoModelFactory as Dmf
import factory
from .factories import SessionTypeFactory
from ..models import SessionType, Session
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site


class TestCaseBase(WebTest):

    def setUp(self):
        flatpage = FlatPage.objects.create(url='/', title='tmp')
        flatpage.sites.set([Site.objects.first()])

    def test_no_auth(self):
        call = self.app.get('/')
        self.assertEqual(call.status, '200 OK')


    def test_auth(self):
        call = self.app.get('/', user='test')
        self.assertEqual(call.status, '200 OK')


class SessionCreation(WebTest):

    def setUp(self):
        flatpage = FlatPage.objects.create(url='/', title='tmp')
        flatpage.sites.set([Site.objects.first()])
        self.session_type = SessionTypeFactory.create()

    def test(self):
        call = self.app.get(reverse('testsession:session_create', kwargs={
            'api_id': self.session_type.api.id
        }), user='admin')
        self.app.reset()
        form = call.forms[1]
        form['session_type'].force_value(value='1')
        response = form.submit(expect_errors=True)

    def test2(self):
        call = self.app.get(reverse('testsession:session_create', kwargs={
            'api_id': self.session_type.api.id
        }), user='admin')
        form = call.forms[1]

        form['session_type'] = self.session_type.id
        form.submit()
        call = self.app.get('/', user='admin')
        assert 'no session' not in str(call.body)

    def test3(self):
        SessionTypeFactory()
        call = self.app.get(reverse('testsession:session_create', kwargs={
            'api_id': self.session_type.api.id
        }), user='admin')
        form = call.forms[1]
        form.submit(expect_errors=True)

    def test4(self):
        call = self.app.get(reverse('testsession:session_create', kwargs={
            'api_id': self.session_type.api.id
        }), user='admin')
        form = call.forms[1]
        form['session_type'].force_value('2')
        form.submit(expect_errors=True)
