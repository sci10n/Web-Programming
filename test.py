import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

import database_helper

MALE = 0
FEMALE = 1


class TwiddlerWelcomeView(unittest.TestCase):
    def setUp(self):
        database_helper.init_db()
        self.driver = webdriver.Firefox()
        self.driver.get("localhost:5000/")
        self.driver.implicitly_wait(1)

    def tearDown(self):
        self.driver.close()

    def test_double_signup(self):

        self.assertTrue(self.signup_user(firstname="Kalle",
                                         lastname="Anka",
                                         gender=MALE,
                                         city="AnkeBorg",
                                         country="USA",
                                         email="kalle@anka.borg",
                                         password="ankeborg",
                                         repassword="ankeborg"))
        self.assertFalse(self.signup_user(firstname="Kalle",
                                          lastname="Anka",
                                          gender=MALE,
                                          city="AnkeBorg",
                                          country="USA",
                                          email="kalle@anka.borg",
                                          password="ankeborg",
                                          repassword="ankeborg"))

    def test_signin(self):
        self.assertFalse(self.signin_user(username="kalle@anka.borg",
                                          password="ankeborg"))

        self.assertTrue(self.signup_user(firstname="Kalle",
                                         lastname="Anka",
                                         gender=MALE,
                                         city="AnkeBorg",
                                         country="USA",
                                         email="kalle@anka.borg",
                                         password="ankeborg",
                                         repassword="ankeborg"))

        self.assertTrue(self.signin_user(username="kalle@anka.borg",
                                         password="ankeborg"))

    def test_invalid_password(self):
        self.assertFalse(self.signup_user(firstname="Kalle",
                                          lastname="Anka",
                                          gender=MALE,
                                          city="AnkeBorg",
                                          country="USA",
                                          email="kalle@anka.borg",
                                          password="ankebor",
                                          repassword="ankebor"))

    def test_invalid_email(self):
        self.assertFalse(self.signup_user(firstname="Kalle",
                                          lastname="Anka",
                                          gender=MALE,
                                          city="AnkeBorg",
                                          country="USA",
                                          email="kalle@anka",
                                          password="ankeborg",
                                          repassword="ankeborg"))

    def test_mismatching_passwords(self):
        self.assertFalse(self.signup_user(firstname="Kalle",
                                          lastname="Anka",
                                          gender=FEMALE,
                                          city="AnkeBorg",
                                          country="USA",
                                          email="kalle@anka.borg",
                                          password="ankeborg",
                                          repassword="ankeborgare"))

    def signup_user(self, firstname, lastname, gender,
                    city, country, email,
                    password, repassword):
        content = self.driver.find_element_by_id("content")
        signup_form = content.find_element_by_id("signupform")

        firstname_input = signup_form.find_element_by_id("firstname")
        firstname_input.clear()
        firstname_input.send_keys(firstname)

        lastname_input = signup_form.find_element_by_id("lastname")
        lastname_input.clear()
        lastname_input.send_keys(lastname)

        gender_select = Select(signup_form.find_element_by_id("gender"))
        gender_select.select_by_index(gender)

        city_input = signup_form.find_element_by_id("city")
        city_input.clear()
        city_input.send_keys(city)

        country_input = signup_form.find_element_by_id("country")
        country_input.clear()
        country_input.send_keys(country)

        email_input = signup_form.find_element_by_id("email")
        email_input.clear()
        email_input.send_keys(email)

        password_input = signup_form.find_element_by_id("password")
        password_input.clear()
        password_input.send_keys(password)

        repassword_input = signup_form.find_element_by_id("repassword")
        repassword_input.clear()
        repassword_input.send_keys(repassword)
        repassword_input.submit()

        time.sleep(1)

        return self.signup_status()

    def signup_status(self):
        email = self.driver.find_element_by_id("signupform").find_element_by_id("email")
        return email.get_attribute('value').encode('utf-8') == ""

    def signin_user(self, username, password):
        content = self.driver.find_element_by_id("content")
        signin_form = content.find_element_by_id("signinform")

        username_input = signin_form.find_element_by_id("username")
        username_input.clear()
        username_input.send_keys(username)

        password_input = signin_form.find_element_by_id("password")
        password_input.clear()
        password_input.send_keys(password)
        password_input.submit()

        time.sleep(1)

        return self.signin_status()

    def signin_status(self):
        success = False

        try:
            self.driver.find_element_by_id("content").find_element_by_id("signinform")
        except NoSuchElementException:
            success = True

        return success


if __name__ == "__main__":
    unittest.main()
