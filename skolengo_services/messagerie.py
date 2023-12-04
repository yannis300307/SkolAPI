import skolengo as skol

from bs4 import BeautifulSoup

class Message:
    """A class used to manage a message from the mailbox."""
    def __init__(self, author, title, title_time, default_time, datetime_format_time, message_origin, has_attachment):
        self.author = author
        self.title = title
        self.title_time = title_time
        self.default_time = default_time
        self.datetime_format_time = datetime_format_time
        self.message_origin = message_origin
        self.has_attachment = has_attachment

        self.content = "NOT IMPLEMENTED YET"


class Messagerie:
    """A class used to manage mailbox, send messages, read messages, etc..."""
    def __init__(self, skolengo: 'skol.Skolengo'):
        """Create an instance of the `Messagerie` class
        You shouldn't use this class Manually. You should get one with `Skolengo().get_service(service)`

        :param skolengo: The Skolengo instance
        """
        self.skolengo = skolengo

    def get_messages_list(self):
        """Retun a list of the last 50 messages"""

        message_list = []

        # Get the mailbox page for scrapping
        content = self.skolengo.ses.get("https://pardailhan.mon-ent-occitanie.fr/sg.do?PROC=MESSAGERIE")
        soup = BeautifulSoup(content.text, features='html.parser')

        message_list_content = soup.find(id="js_boite_reception")
        message_list_html = message_list_content.findAll("li")

        for i in message_list_html:
            author = i.div.span.findAll("span")[-1].get("title")
            title = i.findAll("div", class_="col col--xs-5")[0].span.select(".js-consulterMessage")[0].text
            title = " ".join(title.split("\n")[-1].split())
            time_span = i.findAll("div", {"class": "col--xs-2"})[-1].div.span
            title_time = time_span.get("title")
            default_time = time_span.time.text
            datetime_format_time = time_span.time.get("datetime")
            message_origin = i.findAll("div", {"class": "col--xs-1"})[0].span.span.text
            has_attachment = "icon--attached-file" in i.findAll("div", {"class": "col--xs-1"})[1].span.get("class")

            message_list.append(Message(author, title, title_time, default_time, datetime_format_time,
                                        message_origin, has_attachment))
        return message_list

