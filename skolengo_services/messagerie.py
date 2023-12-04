import skolengo as skol

class Message:
    """A class used to manage a message from the mailbox."""
    def __init__(self):
        self.content = ""

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

        # Get the mailbox page for scrapping
        self.skolengo.ses.get("https://pardailhan.mon-ent-occitanie.fr/sg.do?PROC=MESSAGERIE")
