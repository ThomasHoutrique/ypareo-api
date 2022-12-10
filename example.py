"""
Exeample of using the YPareo unofficial API
The script sends courses from the YPareo platform to a Discord webhook
Author: Thomas Houtrique
License: GNU General Public License v3.0
"""

from datetime import datetime, timedelta
from os import getenv
import httpx
from ypareo_api import YPareo

username = getenv("YPAREO_USER")
password = getenv("YPAREO_PASS")
domain = getenv("YPAREO_DOMAIN")
webhook = getenv("YPAREO_WEBHOOK")
net = YPareo(username=username, password=password, domain=domain)

# Date as day/month/year
date = datetime.today() + timedelta(days=1)
date = date.strftime("%d/%m/%Y")
webhook = {
    "content": f"🌞 <@&1017536399228022845> Voici les cours de demain ({date}) :\nBonne soirée ! 🌙",
    "embeds": [],
    "attachments": [],
}
courses = net.get_tomorrow_courses()
if courses:
    for course in courses:
        course_start_at = timedelta(minutes=int(course["minuteDebut"]))
        course_end_at = course_start_at + timedelta(minutes=int(course["duree"]))
        course = {
            "title": course["libelle"],
            "color": 5814783,
            "fields": [
                {
                    "name": "Horraires",
                    "value": str(course_start_at) + " - " + str(course_end_at),
                },
                # list of details as string separated by \n
                {"name": "Détails", "value": "\n ".join(course["detail"])},
            ],
        }
        webhook["embeds"].append(course)

    r = httpx.post(
        getenv("YPAREO_WEBHOOK"),
        json=webhook,
    )
