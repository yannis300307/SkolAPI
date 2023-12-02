import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from urllib import parse
from enum import Enum


HOST = "https://educonnect.education.gouv.fr"


# Return codes
class ConnectionResult(Enum):
    """An enumeration class used as return code for Educonnect connexion results."""
    SUCCESS = 0
    WRONG_CREDENTIALS = 1    # The sended username or password is wrong
    BAD_PACKET = 2
    ALREADY_CONNECTED = 3
    INVALID_CREDENTIALS = 4  # The username or the password is empty


class DisconnectionResult(Enum):
    """An enumeration class used as return code for Educonnect disconnexion results."""
    SUCCESS = 0
    BAD_PACKET = 1
    NOT_CONNECTED = 2


class EduConnect:
    """A class used to connect and disconnect the Educonnect account."""

    def __init__(self):
        self.ses = requests.session()

        # Headers used to simulate a real navigator
        self.ses.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
        }

    def connect(self, username: str, password: str) -> ConnectionResult:
        """Connect the user to the EduConnect account using the username and the password.

        :param username the EduConnect username of the user
        :param password the EduConnect password of the user

        :return Return a `ConnectionResult` return code
        """
        if username == "" or password == "":
            return ConnectionResult.INVALID_CREDENTIALS
        username = quote_plus(username)
        password = quote_plus(password)

        connect_page = self.ses.get(HOST + "/idp/profile/SAML2/Redirect/SSO?execution=e2s1").text

        soup = BeautifulSoup(connect_page, features="html.parser")

        connect_link = HOST + soup.find(id="validerAuth").get("action")

        connection_result = self.ses.post(connect_link,
                                          data=f"j_username={username}&j_password={password}&_eventId_proceed=",
                                          allow_redirects=False,
                                          headers={"Origin": HOST,
                                                   "Referer": HOST + "/idp/profile/SAML2/Redirect/SSO?execution=e2s1",
                                                   "Content-Type": "application/x-www-form-urlencoded",
                                                   "Sec-Fetch-Site": "same-origin"})

        soup = BeautifulSoup(connection_result.text, features="html.parser")

        relay_state_value = parse.quote(soup.findAll("input", {"name": "RelayState"})[0].get("value"))
        saml_response_value = parse.quote(soup.findAll("input", {"name": "SAMLResponse"})[0].get("value"))

        saml_result = self.ses.post("https://moncompte.educonnect.education.gouv.fr/Shibboleth.sso/SAML2/POST",
                                    data=f"RelayState={relay_state_value}&SAMLResponse={saml_response_value}",
                                    headers={"Origin": HOST,
                                             "Referer": connection_result.url,
                                             "Content-Type": "application/x-www-form-urlencoded",
                                             "Sec-Fetch-Site": "same-origin"})