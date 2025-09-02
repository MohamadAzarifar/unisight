class AuthStrategy:
    def authenticate(self, username, password):
        raise NotImplementedError


class MockAuthStrategy(AuthStrategy):
    def authenticate(self, username, password):
        return username and password and len(username) > 5 and len(password) > 5
