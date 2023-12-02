import requests
import getpass
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from urllib import parse

HOST = "https://educonnect.education.gouv.fr"


class EduConnect:
    def __init__(self):
        self.ses = requests.session()
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

    def connect(self, user_type, username, password):
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

        print(soup)
        relay_state = parse.quote(soup.findAll("input", {"name": "RelayState"})[0].get("value"))
        SAML_response = parse.quote(soup.findAll("input", {"name": "SAMLResponse"})[0].get("value"))

        saml_result = self.ses.post("https://moncompte.educonnect.education.gouv.fr/Shibboleth.sso/SAML2/POST",
                                    data=f"RelayState={relay_state}&SAMLResponse={SAML_response}",
                                    headers={"Origin": HOST,
                                             "Referer": connection_result.url,
                                             "Content-Type": "application/x-www-form-urlencoded",
                                             "Sec-Fetch-Site": "same-origin"})


if __name__ == '__main__':
    edu = EduConnect()
    edu.connect("eleve", input("username ? "), getpass.getpass())
