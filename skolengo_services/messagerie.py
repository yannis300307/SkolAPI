import requests

import skolengo as skol

from bs4 import BeautifulSoup


class ContactList:
    def __init__(self, data: dict, messagerie: 'Messagerie'):
        self.json = data

    def get_contact(self, path):

        path_dir = path.split("/")

        print(self.json)
        print(type(self.json))

        tree = self.json
        contact = None
        for i in path_dir:
            for j in tree:
                if j["text"] == i:
                    if j["text"] == path_dir[-1]:
                        contact = tree
                    else:
                        tree = j["children"]
        return contact



class Discussion:
    def __init__(self, message: 'Message', title_time, default_time, datetime_format_time, author_name, author_type, content_html, raw_soup):
        self.message = message
        self.title_time = title_time
        self.default_time = default_time
        self.datetime_format_time = datetime_format_time
        self.author_name = author_name
        self.author_type = author_type
        self.content_html = content_html

        self.__raw_soup = raw_soup

    def get_content_plain_text(self) -> str:
        """Recover the message content by parsing and convert it to plain text.
        :return: The message content as plain text.
        """
        soup = BeautifulSoup(self.content_html, "html.parser")
        return soup.text

    def get_attachments(self) -> list[str]:
        """Return a list of all atachments of the discussion.

        :return: The attachment list
        """
        attachment_elements_list = self.__raw_soup.select(".js-jumbofiles__file-url")
        attachment_list = []
        for i in attachment_elements_list:
            attachment_list.append(self.message.messagerie.skolengo.get_page_path(i.get("href")[1:]))

        return attachment_list

    content_plain_text = property(get_content_plain_text)
    attachments = property(get_attachments)


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
            time_span = i.div.findAll("div", recursive=False)[1].span
            title_time = time_span.get("title")
            default_time = time_span.time.text
            datetime_format_time = time_span.time.get("datetime")

            author_info = i.div.div.button.div.findAll("div", recursive=False)[1].findAll("div")

            author_name = author_info[0].text
            if len(author_info) > 1:
                author_type = author_info[1].span.text
            else:
                author_type = ""

            content_html = str(i.select(".wysiwyg")[0])

            raw_soup = i

            self.__discussions_list.append(Discussion(self, title_time, default_time, datetime_format_time, author_name, author_type, content_html, raw_soup))

        return self.__discussions_list.copy()

    def get_all_attachment(self) -> list[str]:
        """Return the link to the attachment of the message.

        :return: The link to the attachment or None if there is no attachment
        """
        soup = self.get_message_page()

        attachment_elements_list = soup.select(".js-jumbofiles__file-url")
        attachment_list = []
        for i in attachment_elements_list:
            attachment_list.append(self.messagerie.skolengo.get_page_path(i.get("href")[1:]))

        return attachment_list


class Messagerie:
    """A class used to manage mailbox, send messages, read messages, etc..."""
    def __init__(self, skolengo: 'skol.Skolengo'):
        """Create an instance of the `Messagerie` class
        You shouldn't use this class Manually. You should get one with `Skolengo().get_service(service)`

        :param skolengo: The Skolengo instance
        """
        self.skolengo = skolengo

    def get_contacts(self):
        """Return a `ContactList` object.

        :return: The list of contact"""

        try:
            contact_list_response = self.skolengo.ses.get("https://pardailhan.mon-ent-occitanie.fr/sg.do?PROC=MESSAGERIE&ACTION=GET_NODES&FROM=")
        except requests.ConnectionError:
            return None

        contact_json = contact_list_response.json()

        return ContactList(contact_json, self)

    def get_messages_list(self) -> list[Message]:
        """Return a list of the last 50 messages
        :return: The list of the messages
        """

        message_list = []

        # Get the mailbox page for scrapping
        try:
            content = self.skolengo.ses.get("https://pardailhan.mon-ent-occitanie.fr/sg.do?PROC=MESSAGERIE")
        except requests.ConnectionError:
            return message_list

        try:
            soup = BeautifulSoup(content.text, features='html.parser')
        except UnicodeDecodeError:
            return message_list
        message_list_content = soup.find(id="js_boite_reception")

        if message_list_content is None:
            return message_list

        message_list_html = message_list_content.findAll("li")

        for i in message_list_html:
            # The name of the author
            try:
                author = i.div.span.findAll("span")[-1].get("title")
                if author is None:
                    author = ""
            except (AttributeError, IndexError):
                author = ""

            # The title of the message
            try:
                title = i.findAll("div", class_="col col--xs-5")[0].span.select(".js-consulterMessage")[0].text
                if title is None:
                    title = ""
                title = " ".join(title.split("\n")[-1].split())
            except (AttributeError, IndexError):
                title = ""

            # The time span object used later in this method
            try:
                time_span = i.findAll("div", {"class": "col--xs-2"})[-1].div.span
            except (AttributeError, IndexError):
                time_span = None

            # The title of the time span
            try:
                title_time = time_span.get("title")
                if title_time is None:
                    title_time = ""
            except AttributeError:
                title_time = ""

            # The time written by default on the page
            try:
                default_time = time_span.time.text
                if default_time is None:
                    default_time = ""
            except AttributeError:
                default_time = ""

            # The datetime format of the time
            try:
                datetime_format_time = time_span.time.get("datetime")
                if datetime_format_time is None:
                    datetime_format_time = ""
            except AttributeError:
                datetime_format_time = ""

            # The origin of the message
            try:
                message_origin = i.findAll("div", {"class": "col--xs-1"})[0].span.span.text
                if message_origin is None:
                    message_origin = ""
            except (AttributeError, IndexError):
                message_origin = ""

            # Does the message have an attachment
            try:
                has_attachment = "icon--attached-file" in i.findAll("div", {"class": "col--xs-1"})[1].span.get("class")
                if has_attachment is None:
                    has_attachment = ""
            except (AttributeError, IndexError):
                has_attachment = ""

            # The https link to the message
            try:
                link = i.findAll("div", class_="col col--xs-5")[0].span.select(".js-consulterMessage")[0].get("href")
                if link is None:
                    link = ""
            except (AttributeError, IndexError):
                link = ""

            # Convert the relative path to an absolute path
            link = self.skolengo.get_page_path("sg.do" + link)

            message_list.append(Message(author, title, title_time, default_time, datetime_format_time,
                                        message_origin, has_attachment, link, self))

        return message_list

