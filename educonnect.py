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
    WRONG_CREDENTIALS = 1  # The sended username or password is wrong
    BAD_PACKET = 2
    ALREADY_CONNECTED = 3
    INVALID_CREDENTIALS = 4  # The username or the password is empty
    UNKNOWN_ERROR = 5


class DisconnectionResult(Enum):
    """An enumeration class used as return code for Educonnect disconnexion results."""
    SUCCESS = 0
    BAD_PACKET = 1
    NOT_CONNECTED = 2
    UNKNOWN_ERROR = 3


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

    def is_account_connected(self) -> bool:
        """Return True if the account is connected.

        :return: the connection state
        """

        # Get the account management page
        try:
            account_management_page = self.ses.get(
                "https://moncompte.educonnect.education.gouv.fr/educt-self-service/profil/consultationProfil",
                allow_redirects=False)
        except requests.ConnectionError:
            return False

        # If the account is disconnected, requesting the account management page will try to redirect to
        # the connection page
        return "Location" not in account_management_page.headers

    def connect(self, username: str, password: str) -> ConnectionResult:
        """Connect the user to the EduConnect account using the username and the password.

        :param username: the EduConnect username of the user
        :param password: the EduConnect password of the user

        :return: Return a `ConnectionResult` return code
        """

        # Return if already connected
        if self.is_account_connected():
            return ConnectionResult.ALREADY_CONNECTED

        # Check if the credentials are valid with the same criterias as Educonnect's criterias
        if username == "" or password == "":
            return ConnectionResult.INVALID_CREDENTIALS

        # Quote the credentials
        username = quote_plus(username)
        password = quote_plus(password)

        # Get the connection page to recover connection link and set cookies
        try:
            connect_page = self.ses.get(HOST + "/idp/profile/SAML2/Redirect/SSO?execution=e2s1")
        except requests.ConnectionError:
            return ConnectionResult.BAD_PACKET
        try:
            soup = BeautifulSoup(connect_page.text, features="html.parser")
        except UnicodeDecodeError:
            return ConnectionResult.UNKNOWN_ERROR

        valid_auth_form = soup.find(id="validerAuth")
        if valid_auth_form is None:
            return ConnectionResult.UNKNOWN_ERROR

        connect_link = valid_auth_form.get("action")
        if connect_link is None:
            return ConnectionResult.UNKNOWN_ERROR
        connect_link = HOST + connect_link

        # Send the credentials to the server
        try:
            connection_result = self.ses.post(connect_link,
                                              data=f"j_username={username}&j_password={password}&_eventId_proceed=",
                                              allow_redirects=False,
                                              headers={"Origin": HOST,
                                                       "Referer": HOST+"/idp/profile/SAML2/Redirect/SSO?execution=e2s1",
                                                       "Content-Type": "application/x-www-form-urlencoded",
                                                       "Sec-Fetch-Site": "same-origin"})
        except requests.ConnectionError:
            return ConnectionResult.BAD_PACKET

        # Recover the `RelayState` and `SAMLResponse` values
        try:
            soup = BeautifulSoup(connection_result.text, features="html.parser")
        except UnicodeDecodeError:
            return ConnectionResult.UNKNOWN_ERROR

        relay_state_list = soup.findAll("input", {"name": "RelayState"})
        saml_response_list = soup.findAll("input", {"name": "SAMLResponse"})
        if len(relay_state_list) == 0 or len(saml_response_list) == 0:
            return ConnectionResult.WRONG_CREDENTIALS

        relay_state_value = relay_state_list[0].get("value")
        saml_response_value = saml_response_list[0].get("value")
        if relay_state_value is None or saml_response_value is None:
            return ConnectionResult.UNKNOWN_ERROR

        relay_state_value = parse.quote(relay_state_value)
        saml_response_value = parse.quote(saml_response_value)

        # Post data to the SAML service
        try:
            self.ses.post("https://moncompte.educonnect.education.gouv.fr/Shibboleth.sso/SAML2/POST",
                          data=f"RelayState={relay_state_value}&SAMLResponse={saml_response_value}",
                          headers={"Origin": HOST,
                                   "Referer": connection_result.url,
                                   "Content-Type": "application/x-www-form-urlencoded",
                                   "Sec-Fetch-Site": "same-origin"})
        except requests.ConnectionError:
            return ConnectionResult.BAD_PACKET

        # Check if the connection is effective
        return ConnectionResult.SUCCESS if self.is_account_connected() else ConnectionResult.UNKNOWN_ERROR

    def disconnect(self) -> DisconnectionResult:
        """Disconnect the EduConnect account.

        :return: the disconnection state"""

        # Return if the account is not connected
        if not self.is_account_connected():
            return DisconnectionResult.NOT_CONNECTED

        # Get the disconnection point
        try:
            self.ses.get("https://moncompte.educonnect.education.gouv.fr/educt-self-service/connexion/deconnexion")
        except requests.ConnectionError:
            return DisconnectionResult.BAD_PACKET

        # Check if the disconnection is effective
        return DisconnectionResult.SUCCESS if not self.is_account_connected() else DisconnectionResult.UNKNOWN_ERROR
