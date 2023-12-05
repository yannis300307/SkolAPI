import getpass

from educonnect import EduConnect
from skolengo import Skolengo, SkolengoService

if __name__ == '__main__':
    edu = EduConnect()

    edu.connect(input("username ? "), getpass.getpass())

    skol = Skolengo("", "")

    skol.connect_educonnect(edu, "TOULO-EDU_parent_eleve")

    # Code here
    mailbox = skol.get_service(SkolengoService.MESSAGERIE)
    msg_list = mailbox.get_messages_list()

    print(msg_list[0].get_discussion_list()[0].content_html)

    print(msg_list[12].get_discussion_list()[0].get_attachments())

    skol.disconnect()
    edu.disconnect()
