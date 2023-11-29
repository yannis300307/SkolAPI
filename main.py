import requests
import getpass
from urllib.parse import quote_plus

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
        """
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
        Accept-Language: fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3
        Accept-Encoding: gzip, deflate, br
        Connection: keep-alive
        Upgrade-Insecure-Requests: 1
        Sec-Fetch-Dest: document
        Sec-Fetch-Mode: navigate
        Sec-Fetch-Site: none
        Sec-Fetch-User: ?1"""

    def connect(self, user_type, username, password):
        username = quote_plus(username)
        password = quote_plus(password)
        print(username, password)

        print(self.ses.get("https://educonnect.education.gouv.fr/idp/profile/SAML2/Redirect/SSO?execution=e2s1"))
        print(self.ses.cookies)
        #self.ses.cookies["profilEduConnect"] = user_type

        print(self.ses.post("https://educonnect.education.gouv.fr/idp/profile/SAML2/POST/SSO?execution=e1s2",
                            data=f"j_username={username}&j_password={password}&_eventId_proceed=").text)

        print(self.ses.cookies)


if __name__ == '__main__':
    edu = EduConnect()
    edu.connect("eleve", input("username ? "), input("mdp ? ")) # getpass.getpass())
