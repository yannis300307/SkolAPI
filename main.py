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
    mailbox.get_messages_list()

    skol.disconnect()
    edu.disconnect()
