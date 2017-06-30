from aleph.tests.util import TestCase
from aleph.tests.factories.models import RoleFactory


class SessionsApiTestCase(TestCase):

    def setUp(self):
        super(SessionsApiTestCase, self).setUp()
        self.role = RoleFactory.create()

    def test_session_anonymous(self):
        res = self.client.get('/api/2/sessions')
        assert res.status_code == 200, res
        assert not res.json['logged_in'], res.json
        assert 'role' not in res.json, res.json

    def test_session_with_user(self):
        role = self.login(is_admin=True)
        res = self.client.get('/api/2/sessions')
        print res.json
        assert res.json['logged_in'], res.json
        assert res.json['role']['id'] == role.id, res.json

    def test_status_get_with_password_registration_enabled(self):
        res = self.client.get('/api/2/sessions')
        assert res.status_code == 200, res
        assert len(res.json['providers']) == 1, res
        assert res.json['providers'][0]['name'] == 'password', res
        assert res.json['providers'][0]['registration'], res

    def test_status_get_with_password_registration_disabled(self):
        self.app.config['PASSWORD_REGISTRATION'] = False

        res = self.client.get('/api/2/sessions')
        assert res.status_code == 200, res
        assert len(res.json['providers']) == 1, res
        assert res.json['providers'][0]['name'] == 'password', res
        assert not res.json['providers'][0]['registration'], res

    def test_status_get_without_password_login(self):
        self.app.config['PASSWORD_LOGIN'] = False

        res = self.client.get('/api/2/sessions')
        assert res.status_code == 200, res
        assert len(res.json['providers']) == 0, res

    def test_password_login_get(self):
        res = self.client.get('/api/2/sessions/login/password')
        assert res.status_code == 404, res

    def test_password_login_post_no_data(self):
        res = self.client.post('/api/2/sessions/login/password')
        assert res.status_code == 404, res

    def test_password_login_post_good_email_and_password(self):
        secret = self.fake.password()
        self.role.set_password(secret)
        data = dict(email=self.role.email, password=secret)

        res = self.client.post('/api/2/sessions/login/password', data=data)

        assert res.status_code == 200, res
        assert res.json['role']['id'] == self.role.id, res
        assert res.json['api_key'] == self.role.api_key, res
