from enum import Enum

from educonnect import EduConnect


class ConnectionResult(Enum):
    SUCCESS = 0


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

    def get_page_path(self, relat_path: str) -> str:
        """Return the absolute URL to the given relative path.
        :param relat_path: The relative path

        :return: the absolute path
        """

        return f"https://{self.sub_ent}.{self.host}/{relat_path}"

    def connect_educonnect(self, educonnect: EduConnect) -> bool:
        """Connect the ENT with Educonnect.
        :param educonnect: The autheticated Educonnect instance

        :return: Connection state
        """

        # Link the Skolengo session to the EduConnect session
        self.ses = educonnect.ses

        # Get the login page
        self.ses.get(f"https://cas.{self.host}.fr/login")

        return True

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
