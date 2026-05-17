from unittest.mock import MagicMock, patch
import pytest
from werkzeug.security import generate_password_hash

from app.service.authservice import AuthService


class TestNormalizeRole:
    def test_maps_legacy_normal_role_to_standard_user(self):
        assert AuthService.normalize_role("normal") == "standard_user"

    def test_preserves_standard_user(self):
        assert AuthService.normalize_role("standard_user") == "standard_user"

    def test_preserves_admin_role(self):
        assert AuthService.normalize_role("admin") == "admin"


@pytest.mark.usefixtures("flask_app_ctx")
class TestSigninUser:
    def test_rejects_missing_credentials(self):
        user, err = AuthService.signin_user(" ", "secret")
        assert user is None
        assert err == "Please fill in all the fields."

        user, err = AuthService.signin_user("alice.nguyen@student.uwa.edu.au", "")
        assert user is None
        assert err == "Please fill in all the fields."

    def test_rejects_unknown_user(self):
        q = MagicMock()
        q.first.return_value = None
        with patch("app.service.authservice.User.query") as uq:
            uq.filter_by.return_value = q
            user, err = AuthService.signin_user("nobody99999@student.uwa.edu.au", "x")
        assert user is None
        assert err == "User does not exist"

    def test_rejects_wrong_password(self):
        existing = MagicMock()
        existing.password = generate_password_hash("correct")
        q = MagicMock()
        q.first.return_value = existing
        with patch("app.service.authservice.User.query") as uq:
            uq.filter_by.return_value = q
            user, err = AuthService.signin_user("someone.user@student.uwa.edu.au", "wrong")
        assert user is None
        assert err == "Incorrect password"

    def test_returns_user_when_password_matches(self):
        existing = MagicMock()
        existing.password = generate_password_hash("correct")
        q = MagicMock()
        q.first.return_value = existing
        with patch("app.service.authservice.User.query") as uq:
            uq.filter_by.return_value = q
            user, err = AuthService.signin_user(
                "Someone.User@Student.UWA.EDU.AU",
                "correct",
            )
        assert user is existing
        assert err is None
        uq.filter_by.assert_called_once_with(email="someone.user@student.uwa.edu.au")


@pytest.mark.usefixtures("flask_app_ctx")
class TestSignupUser:
    def test_rejects_blank_fields(self):
        user, err = AuthService.signup_user("", "Last", "22345678@student.uwa.edu.au", "pw")
        assert user is None
        assert err == "Please fill in all the fields."

    def test_rejects_duplicate_email(self):
        q = MagicMock()
        q.first.return_value = MagicMock()
        with patch("app.service.authservice.User.query") as uq:
            uq.filter_by.return_value = q
            user, err = AuthService.signup_user("A", "B", "27654321@student.uwa.edu.au", "pw")
        assert user is None
        assert err == "An account with that email already exists."

    def test_rejects_non_student_uwa_email(self):
        user, err = AuthService.signup_user("A", "B", "user@gmail.com", "pw")
        assert user is None
        assert err == "Use UWA student email format: 8digits@student.uwa.edu.au."

    def test_creates_user_and_commits_when_email_free(self):
        q = MagicMock()
        q.first.return_value = None
        session_mock = MagicMock()
        # Patch only User (not User.query): patching both replaces the class and drops the query mock.
        with (
            patch("app.service.authservice.User") as UserCls,
            patch("app.service.authservice.db.session", session_mock),
            patch("app.service.authservice.LoggingService.log_action") as log_action_mock,
        ):
            UserCls.query.filter_by.return_value = q
            UserCls.return_value = MagicMock()

            user, err = AuthService.signup_user(
                "  Ada ",
                " Lovelace ",
                " 22344321@student.uwa.edu.au ",
                "secret123",
            )

        assert err is None
        assert user is UserCls.return_value
        session_mock.add.assert_called_once_with(user)
        session_mock.commit.assert_called_once()
        log_action_mock.assert_called_once()
        UserCls.assert_called_once()
        kwargs = UserCls.call_args.kwargs
        assert kwargs["email"] == "22344321@student.uwa.edu.au"
        assert kwargs["first_name"] == "Ada"
        assert kwargs["last_name"] == "Lovelace"
        assert kwargs["role"] == "standard_user"


class TestLoginAndLogoutUser:
    def test_login_user_sets_session_fields(self, app_ctx):
        user = MagicMock()
        user.user_id = 42
        user.first_name = "Sam"
        user.last_name = "River"
        user.role = "standard_user"

        with patch("app.service.authservice.AuthService.normalize_role", side_effect=lambda r: r):
            with patch("app.service.authservice.db.session") as session_mock:
                AuthService.login_user(user)

        session_mock.commit.assert_not_called()
        from flask import session

        assert session["user_id"] == 42
        assert session["user_name"] == "Sam"
        assert session["user_role"] == "standard_user"
        assert session["user_initials"] == "SR"

    def test_logout_user_clears_session(self, app_ctx):
        from flask import session

        session["user_id"] = 1
        AuthService.logout_user()
        assert dict(session) == {}


@pytest.mark.usefixtures("flask_app_ctx")
class TestChangePassword:
    def test_user_not_found_returns_message(self):
        with patch("app.service.authservice.User.query") as uq:
            uq.get.return_value = None
            msg = AuthService.change_password(99, "a", "b", "b")
        assert msg == "User not found."

    def test_missing_fields_returns_validation_message(self):
        user = MagicMock()
        with patch("app.service.authservice.User.query") as uq:
            uq.get.return_value = user
            msg = AuthService.change_password(1, "", "new", "new")
        assert msg == "Please fill in all password fields."

    def test_mismatch_between_new_and_confirm(self):
        user = MagicMock()
        with patch("app.service.authservice.User.query") as uq:
            uq.get.return_value = user
            msg = AuthService.change_password(1, "old", "new", "different")
        assert msg == "New password and confirm password do not match."

    def test_wrong_current_password(self):
        user = MagicMock()
        user.password = generate_password_hash("actual-old")
        with patch("app.service.authservice.User.query") as uq:
            uq.get.return_value = user
            msg = AuthService.change_password(1, "wrong-old", "new", "new")
        assert msg == "Current password is incorrect."

    def test_success_updates_hash_and_commits(self):
        user = MagicMock()
        user.password = generate_password_hash("old-secret")
        session_mock = MagicMock()
        with (
            patch("app.service.authservice.User.query") as uq,
            patch("app.service.authservice.db.session", session_mock),
        ):
            uq.get.return_value = user
            msg = AuthService.change_password(1, "old-secret", "new-secret", "new-secret")

        assert msg is None
        session_mock.commit.assert_called_once()
        assert user.password != generate_password_hash("old-secret")
