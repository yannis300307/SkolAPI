from enum import Enum
from urllib import parse

import requests

from educonnect import EduConnect
from bs4 import BeautifulSoup


class ConnectionResult(Enum):
    SUCCESS = 0
    BAD_PACKET = 1
    UNKNOWN_ERROR = 2
    EDUCONNECT_NOT_CONNECTED = 3
    ALREADY_CONNECTED = 4

class ConnectionType(Enum):
    NOT_CONNECTED = 0
    EDUCONNECT = 1
    DEFAULT_CAS = 2


class Skolengo:
    """A class used to interact with Skolengo."""
    def __init__(self, service_host: str, sub_ent: str):
        """Create an insance on Skolengo.
        :param service_host: the ENT domain such as : `mon-ent-occitanie.fr`
        :param sub_ent: the subdomain name such as `cite-narbonne`
        """
        self.host = service_host
        self.sub_ent = sub_ent
        self.ses = None
        self.connection_type = None

    def get_page_path(self, relat_path: str) -> str:
        """Return the absolute URL to the given relative path.
        :param relat_path: The relative path

        :return: the absolute path
        """

        return f"https://{self.sub_ent}.{self.host}/{relat_path}"

    def connect_educonnect(self, educonnect: EduConnect, user_type: str) -> ConnectionResult:
        """Connect the ENT with Educonnect.
        :param educonnect: The autheticated Educonnect instance

        :return: Connection state
        """

        # Link the Skolengo session to the EduConnect session
        self.ses = educonnect.ses

        # Get the login page
        try:
            self.ses.get(f"https://cas.{self.host}/login?service=" + self.get_page_path('sg.do?PROC=IDENTIFICATION_FRONT'))
            submit_result = self.ses.get(f"https://cas.{self.host}/login?selection={user_type}&service={parse.quote_plus(self.get_page_path('sg.do?PROC=IDENTIFICATION_FRONT'))}&submit=Valider")
        except requests.ConnectionError:
            return ConnectionResult.BAD_PACKET

        try:
            soup = BeautifulSoup(submit_result.text, features="html.parser")
        except UnicodeDecodeError:
            return ConnectionResult.UNKNOWN_ERROR

        relay_state_list = soup.findAll("input", {"name": "RelayState"})
        saml_request_list = soup.findAll("input", {"name": "SAMLRequest"})
        if len(relay_state_list) == 0 or len(saml_request_list) == 0:
            return ConnectionResult.UNKNOWN_ERROR

        relay_state_value = relay_state_list[0].get("value")
        saml_request_value = saml_request_list[0].get("value")
        if relay_state_value is None or saml_request_value is None:
            return ConnectionResult.UNKNOWN_ERROR

        relay_state_value = parse.quote_plus(relay_state_value)
        saml_request_value = parse.quote_plus(saml_request_value)
        try:
            sso_result = self.ses.post("https://educonnect.education.gouv.fr/idp/profile/SAML2/POST/SSO",
                          data=f"RelayState={relay_state_value}&SAMLRequest={saml_request_value}",
                                       headers={
                                           "Content-Type": "application/x-www-form-urlencoded",
                                           "Referer": f"https://cas.{self.host}/",
                                           "Origin": f"https://cas.{self.host}",
                                           "Sec-Fetch-Site": "cross-site"
                                       })
        except requests.ConnectionError:
            return ConnectionResult.BAD_PACKET

        try:
            soup = BeautifulSoup(sso_result.text, features="html.parser")
        except UnicodeDecodeError:
            return ConnectionResult.UNKNOWN_ERROR

        relay_state_list = soup.findAll("input", {"name": "RelayState"})
        saml_response_list = soup.findAll("input", {"name": "SAMLResponse"})
        if len(relay_state_list) == 0 or len(saml_response_list) == 0:
            return ConnectionResult.UNKNOWN_ERROR

        relay_state_value = relay_state_list[0].get("value")
        saml_response_value = saml_response_list[0].get("value")
        if relay_state_value is None or saml_response_value is None:
            return ConnectionResult.UNKNOWN_ERROR

        relay_state_value = parse.quote(relay_state_value)
        saml_response_value = parse.quote(saml_response_value)

        try:
            self.ses.post("https://cas.mon-ent-occitanie.fr/saml/SAMLAssertionConsumer",
                          data=f"RelayState={relay_state_value}&SAMLResponse={saml_response_value}",
                          headers={
                               "Content-Type": "application/x-www-form-urlencoded",
                               "Referer": "https://educonnect.education.gouv.fr/",
                               "Origin": "https://educonnect.education.gouv.fr",
                               "Sec-Fetch-Site": "cross-site"
                           })
        except requests.ConnectionError:
            return ConnectionResult.BAD_PACKET

        return ConnectionResult.SUCCESS

    def connect_cas(self, username: str, password: str) -> bool:
        """Connect the ENT with direct CAS connection.

        :param username: The account username
        :param password: The account password

        :return: Connection state
        """


    def disconnect(self) -> bool:
        """Disconnect the ENT.

        :return: Disconnection result
        """
