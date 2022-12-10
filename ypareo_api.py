"""
YPareo unofficial API written in Python
Author: Thomas Houtrique
License: GNU General Public License v3.0
"""
import json
from datetime import datetime
import httpx
from bs4 import BeautifulSoup


class YPareo:
    """
    YPareo API functions
    """

    def __init__(self, username: str, password: str, domain: str):
        self.session = httpx.Client()
        self.domain = domain
        self.data = {
            "login": username,
            "password": password,
            "screenWidth": "1920",
            "screenHeight": "1080",
            "btnSeConnecter": "Se connecter",
        }
        self.login()

    def __get_csrf(self):
        """
        Get CSRF token function
        1. We retrieve the HTML of the login page
        2. We extract the "token_csrf" field value, which is the CSRF token
        3. We return the token
        """
        csrf_req = self.session.get(f"{self.domain}/index.php/login/")
        if csrf_req.status_code != 200:
            raise Exception("Failed to get CSRF token, error :" + csrf_req.status_code)
        soup = BeautifulSoup(csrf_req.text, "html.parser")
        csrf = soup.find("input", {"name": "token_csrf"})["value"]
        return csrf

    def login(self):
        """
        Login function
        1. It sends a request to the login page with the data (email, password and the csrf token) and gets a cookie named IntNum.
        2. Then, it gets the home page with the IntNum cookie and checks if the response was successful.
        3. If the response was successful, we exit the function
        """
        self.data["token_csrf"] = self.__get_csrf()
        login_req = self.session.post(
            f"{self.domain}/index.php/authentication/",
            data=self.data,
        )
        if login_req.status_code != 303:
            raise Exception("Failed to login, error :" + login_req.status_code)

        int_num = login_req.headers.get("Set-Cookie").split(";")[0].split("=")[1]
        self.session.cookies.set("IntNum", int_num)
        home_req = self.session.get(f"{self.domain}/index.php/apprenant/accueil")
        if home_req.status_code != 200:
            raise Exception("Failed to get home page, error :" + home_req.status_code)

    def get_week_planning(self, week: int = None):
        """
        Get week planning function
        1. We create a get_week_planning function to get the planning of the current week.
        2. We check if the week argument is not None (if it is not None, then it means that we want to get the planning of a specific week).
        3. If the week argument is not None, then we create a url variable that contains the url to get the planning of the week (the value of the week argument is added to the url). If the week argument is None, then we create a url variable that contains the url to get the planning of the current week.
        4. We create a planning_req variable that contains the result of the get request to the url variable.
        5. We return the json data of the planning (we use the split() method to get the json data and we use the json.loads() method to return the json data)
        """
        current_year = datetime.now().year
        if week:
            url = f"{self.domain}/index.php/apprenant/planning/courant/?semaineDebut={str(current_year) + str(week + 1)}&modeAffichage=0"
        else:
            url = f"{self.domain}/index.php/apprenant/planning/courant/"
        planning_req = self.session.get(url)
        if planning_req.status_code != 200:
            raise Exception(
                "Failed to get planning, error :" + planning_req.status_code
            )
        return json.loads(
            planning_req.text.split("var planningJSON        = ")[1].split("]};")[0]
            + "]}"
        )

    def get_tomorrow_courses(self):
        """
        Get tomorrow function
        1. Get the current day number
        2. If the day is sunday, set the day number to monday (1) and the week number to the next week
        3. Else, get the current week number
        4. For each course in the current day, add it to the list
        5. Return the list of courses, which will be used in the next function
        """
        tomorrow_courses = []
        day_number: int = datetime.today().weekday() + 2
        if day_number == 8:
            day_number = 1
            planning_json = self.get_week_planning(week=datetime.now().isocalendar()[1])
        else:
            planning_json = self.get_week_planning()
        for i in planning_json["semaines"][0]["ressources"][0]["seances"]:
            if int(i["numJour"]) == int(day_number):
                tomorrow_courses.append(i)
        if not tomorrow_courses:
            return None
        return tomorrow_courses
