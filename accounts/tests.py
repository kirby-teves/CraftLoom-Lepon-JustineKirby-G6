from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountTests(TestCase):
    def setUp(self):
        self.artisan = User.objects.create_user("maria", "maria@example.com", "Str0ng!Pass99", first_name="Maria", last_name="Santos")
        self.admin = User.objects.create_user("boss", "boss@example.com", "Str0ng!Pass99", role=User.Role.ADMIN)

    def reg(self, **over):
        data = {"username": "juan", "first_name": "Juan", "last_name": "Cruz", "email": "juan@example.com",
                "password1": "Str0ng!Pass99", "password2": "Str0ng!Pass99"}
        data.update(over)
        return self.client.post(reverse("register"), data)

    def test_register_success_hashes_password_and_assigns_artisan(self):
        r = self.reg()
        self.assertRedirects(r, reverse("dashboard"), fetch_redirect_response=False)
        u = User.objects.get(username="juan")
        self.assertEqual(u.role, User.Role.ARTISAN)
        self.assertNotEqual(u.password, "Str0ng!Pass99")
        self.assertTrue(u.password.startswith("pbkdf2_"))

    def test_register_validation(self):
        for bad in ({"password2": "nope"}, {"email": "not-an-email"}, {"email": "MARIA@example.com"},
                    {"username": "Maria"}, {"first_name": ""}):
            r = self.reg(**bad)
            self.assertEqual(r.status_code, 200, bad)
            self.assertFalse(User.objects.filter(username="juan").exists(), bad)

    def test_login_logout(self):
        r = self.client.post(reverse("login"), {"username": "maria", "password": "Str0ng!Pass99"})
        self.assertRedirects(r, reverse("dashboard"), fetch_redirect_response=False)
        self.client.post(reverse("logout"))
        r = self.client.post(reverse("login"), {"username": "maria", "password": "wrong"})
        self.assertContains(r, "Invalid username/email or password")
        self.client.login(username="maria", password="Str0ng!Pass99")
        self.client.post(reverse("logout"))
        self.assertRedirects(self.client.get(reverse("profile")), "/login/?next=/profile/")

    def test_login_with_email(self):
        self.assertTrue(self.client.login(username="maria@example.com", password="Str0ng!Pass99"))

    def test_protected_pages_redirect_when_logged_out(self):
        for name in ("dashboard", "artisan_dashboard", "admin_dashboard", "profile", "profile_edit"):
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302)
            self.assertIn("/login/", r["Location"])

    def test_role_dashboards(self):
        self.client.login(username="maria", password="Str0ng!Pass99")
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("artisan_dashboard"))
        r = self.client.get(reverse("admin_dashboard"))
        self.assertRedirects(r, reverse("artisan_dashboard"))
        self.client.logout()
        self.client.login(username="boss", password="Str0ng!Pass99")
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("admin_dashboard"))
        self.assertRedirects(self.client.get(reverse("artisan_dashboard")), reverse("admin_dashboard"))

    def test_profile_edit_own_only(self):
        self.client.login(username="maria", password="Str0ng!Pass99")
        r = self.client.post(reverse("profile_edit"), {"first_name": "Mia", "last_name": "Santos",
                             "email": "mia@example.com", "contact_number": "0917 123 4567", "business_name": "Mia Crafts"})
        self.assertRedirects(r, reverse("profile"))
        self.artisan.refresh_from_db()
        self.assertEqual(self.artisan.first_name, "Mia")
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.email, "boss@example.com")

    def test_profile_email_must_be_unique(self):
        self.client.login(username="maria", password="Str0ng!Pass99")
        r = self.client.post(reverse("profile_edit"), {"first_name": "M", "last_name": "S", "email": "boss@example.com"})
        self.assertEqual(r.status_code, 200)
        self.artisan.refresh_from_db()
        self.assertEqual(self.artisan.email, "maria@example.com")

    def test_cannot_self_assign_admin_role(self):
        self.client.login(username="maria", password="Str0ng!Pass99")
        self.client.post(reverse("profile_edit"), {"first_name": "M", "last_name": "S", "email": "maria@example.com", "role": "admin"})
        self.artisan.refresh_from_db()
        self.assertEqual(self.artisan.role, User.Role.ARTISAN)
