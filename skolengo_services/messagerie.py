import requests

import skolengo as skol

from bs4 import BeautifulSoup


class Discussion:
    def __init__(self, message: 'Message', title_time, default_time, datetime_format_time, author_name, author_type, content_html):
        self.message = message

        self.message.messagerie.skolengo.ses.get()

class Message:
    """A class used to manage a message from the mailbox."""
    def __init__(self, author: str, title: str, title_time: str, default_time: str,
                 datetime_format_time: str, message_origin: str, has_attachment: bool,
                 link: str, messagerie: 'Messagerie'):

        self.author = author
        self.title = title
        self.title_time = title_time
        self.default_time = default_time
        self.datetime_format_time = datetime_format_time
        self.message_origin = message_origin
        self.has_attachment = has_attachment
        self.link = link

        self.messagerie = messagerie

        self.__discussions_list = []
        self.__reading_page_soup = None

    def get_message_page(self) -> BeautifulSoup | None:
        """Return the BeautifulSoup object of the message reading page.

        :return: The soup or None if any error happened
        """
        if self.__reading_page_soup is not None:
            return self.__reading_page_soup

        try:
            message_content_page = self.messagerie.skolengo.ses.get(self.link)
        except requests.ConnectionError:
            return None

        try:
            soup = BeautifulSoup(message_content_page.text, features="html.parser")
        except UnicodeDecodeError:
            return None

        self.__reading_page_soup = soup

        return soup

    def get_discussion_list(self) -> list[Discussion]:
        """Recover the discussions.
        :return: The discussion list
        """

        soup = self.get_message_page()
        if soup is None:
            return []

        if self.__discussions_list:
            return self.__discussions_list.copy()

        discussions = soup.select(".js-message")

        for i in discussions:
            soup.find()
            time_span = i.div.find("div")[1].span
            title_time = time_span.get("title")
            default_time = time_span.time.text
            datetime_format_time = time_span.time.get("datetime")

            author_info = i.div.div.button.div.find("div")[1].find("div")

            author_name = author_info[0].text
            author_type = author_info[1].span.text

            content_html = i.find("div", class_="row")[0].div

            self.__discussions_list.append(Discussion(title_time, default_time, datetime_format_time, author_name, author_type, content_html))

    def get_content_plain_text(self) -> str:
        """Recover the message content by parsing and convert it to plain text.
        :return: The message content as plain text.
        """
        soup = BeautifulSoup(self.get_content(), "html.parser")
        return soup.text

    def get_attachment(self) -> list[str]:
        """Return the link to the attachment of the message.

        :return: The link to the attachment or None if there is no attachment
        """
        soup = self.get_message_page()

        attachment_elements_list = soup.select(".js-jumbofiles__file-url")
        attachment_list = []
        for i in attachment_elements_list:
            attachment_list.append(self.messagerie.skolengo.get_page_path(i.get("href")[1:]))

        return attachment_list

    #content = property(get_content)
    content_plain_text = property(get_content_plain_text)


class Messagerie:
    """A class used to manage mailbox, send messages, read messages, etc..."""
    def __init__(self, skolengo: 'skol.Skolengo'):
        """Create an instance of the `Messagerie` class
        You shouldn't use this class Manually. You should get one with `Skolengo().get_service(service)`

        :param skolengo: The Skolengo instance
        """
        self.skolengo = skolengo

    def get_messages_list(self):
        """Return a list of the last 50 messages"""

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
            link = i.findAll("div", class_="col col--xs-5")[0].span.select(".js-consulterMessage")[0].get("href")
            link = self.skolengo.get_page_path("sg.do" + link)

            message_list.append(Message(author, title, title_time, default_time, datetime_format_time,
                                        message_origin, has_attachment, link, self))

        return message_list

