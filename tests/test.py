import unittest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import random


def setUpRun():
    """Will be executed first"""
    global driver
    options = Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(10)
    driver.maximize_window()


def tearDownRun():
    """Will be executed last"""
    driver.quit()


def fillOwnerData():
    """Helper function for filling data in e_CorrectNewOwnerData and e_IncorrectNewOwnerData"""
    firstname = driver.find_element_by_id("firstName")
    lastname = driver.find_element_by_id("lastName")
    address = driver.find_element_by_id("address")
    city = driver.find_element_by_id("city")
    telephone = driver.find_element_by_id("telephone")
    fake = Faker()
    firstname.clear()
    firstname.send_keys(fake.first_name())
    lastname.clear()
    lastname.send_keys(fake.last_name())
    address.clear()
    address.send_keys(fake.address())
    city.clear()
    city.send_keys(fake.city())
    telephone.clear()
    # Does not fill telephone field


class PetClinic(unittest.TestCase):

    def setUpModel(self):
        """Will be executed first in this model"""
        pass

    def tearDownModel(self):
        """Will be executed last in this model"""
        pass

    # ------------------------------ EDGES (implements actions) ----------------------------------------------

    def e_AddNewPet(self):
        driver.find_element_by_link_text("Add New Pet").click()

    def e_AddNewPetFailed(self):
        birthdate = driver.find_element_by_id("birthDate")
        birthdate.clear()
        birthdate.send_keys("2015/02/05" + Keys.ENTER)
        name = driver.find_element_by_id("name")
        name.clear()
        # No name given
        wait = WebDriverWait(driver, 10)    # Waits for datepicker to have disappeared
        wait.until(EC.invisibility_of_element((By.ID, "ui-datepicker-div")))
        animal = Select(driver.find_element_by_id("type"))
        animal.select_by_visible_text("dog")
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def e_AddNewPetSuccessful(self):
        birthdate = driver.find_element_by_id("birthDate")
        birthdate.clear()
        birthdate.send_keys("2015/02/05" + Keys.ENTER)
        name = driver.find_element_by_id("name")
        name.clear()
        name.send_keys(Faker().first_name())
        wait = WebDriverWait(driver, 10)    # Waits for datepicker to have disappeared
        wait.until(EC.invisibility_of_element((By.ID, "ui-datepicker-div")))
        animal = Select(driver.find_element_by_id("type"))
        animal.select_by_visible_text("dog")
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def e_AddOwner(self):
        driver.find_element_by_link_text("Add Owner").click()

    def e_AddVisit(self):
        driver.find_element_by_link_text("Add Visit").click()

    def e_AddVisitFailed(self):
        description = driver.find_element_by_id("description")
        description.clear()
        # No description given
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def e_AddVisitSuccessful(self):
        description = driver.find_element_by_id("description")
        description.clear()
        description.send_keys(Faker().word())
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def e_ClearSearchVeterinarians(self):
        search_box = driver.find_element_by_xpath("//input[@type='search']")
        search_box.clear()

    def e_CorrectNewOwnerData(self):
        fillOwnerData()     # Fills in everything except phone field
        telephone = driver.find_element_by_id("telephone")
        telephone.send_keys(random.randint(0, 9999999999))  # Random phone number with max 10 digits
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def e_EditPet(self):
        driver.find_element_by_link_text("Edit Pet").click()

    def e_FindOwners(self):
        driver.find_element_by_class_name("icon-search").click()

    def e_HomePage(self):
        driver.find_element_by_class_name("icon-home").click()

    def e_IncorrectNewOwnerData(self):
        fillOwnerData()     # Fills in everything except phone field
        telephone = driver.find_element_by_id("telephone")
        telephone.send_keys(random.randint(10000000000, 99999999999))   # Random phone number with over 10 digits
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def e_NewOwnerFailed(self):
        """This function is only for returning to vertex."""
        pass

    def e_SearchOwners(self):
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def e_SearchVeterinarians(self):
        search_box = driver.find_element_by_xpath("//input[@type='search']")
        search_box.clear()
        search_box.send_keys("Helen")

    def e_UpdatePet(self):
        name = driver.find_element_by_id("name")
        name.clear()
        name.send_keys(Faker().first_name())
        driver.find_element_by_xpath("//button[@type='submit']").click()

    def e_Veterinarians(self):
        driver.find_element_by_class_name("icon-th-list").click()

    def e_startBrowser(self):
        driver.get("http://localhost:9966/petclinic/")

    # ------------------------------ VERTICES (implements tests) --------------------------------------------

    def v_FindOwners(self):
        heading = driver.find_element_by_tag_name("h2")
        self.assertEqual(heading.text, "Find Owners")

    def v_HomePage(self):
        heading = driver.find_element_by_tag_name("h2")
        self.assertEqual(heading.text, "Welcome")

    def v_IncorrectNewOwnerData(self):
        # e_IncorrectNewOwnerData fills in a phone number over 10 digits
        message = driver.find_element_by_css_selector("div.control-group.error > div.controls > span.help-inline")
        self.assertEqual(message.text, "numeric value out of bounds (<10 digits>.<0 digits> expected)")

    def v_NewOwner(self):
        heading = driver.find_element_by_tag_name("h2")
        self.assertEqual(heading.text, "New Owner")

    def v_NewPet(self):
        heading = driver.find_element_by_tag_name("h2")
        self.assertEqual(heading.text, "New Pet")

    def v_NewVisit(self):
        heading = driver.find_element_by_tag_name("h2")
        self.assertEqual(heading.text, "New Visit")

    def v_OwnerInformation(self):
        heading = driver.find_element_by_tag_name("h2")
        self.assertEqual(heading.text, "Owner Information")

    def v_Owners(self):
        heading = driver.find_element_by_tag_name("h2")
        self.assertEqual(heading.text, "Owners")

    def v_Pet(self):
        heading = driver.find_element_by_tag_name("h2")
        self.assertEqual(heading.text, "Pet")

    def v_SearchResult(self):
        # e_SearchVeterinarians searches for "helen"
        search_result = driver.find_element_by_xpath("//table[@id='vets']/tbody/tr")
        self.assertIn("Helen Leary", search_result.text)

    def v_Veterinarians(self):
        heading = driver.find_element_by_tag_name("h2")
        self.assertEqual(heading.text, "Veterinarians")
