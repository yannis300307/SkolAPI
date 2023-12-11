import getpass

from educonnect import EduConnect, ConnectionResult as EduResult
from skolengo import Skolengo, SkolengoService, ConnectionResult as Skoresult

if __name__ == '__main__':
    edu = EduConnect()

    print("Educonnect :")
    match edu.connect(input("username ? "), getpass.getpass()):
        case EduResult.SUCCESS:
            print("SUCCESS")
        case EduResult.UNKNOWN_ERROR:
            print("UNKNOWN_ERROR")
        case EduResult.BAD_PACKET:
            print("BAD_PACKET")
        case EduResult.ALREADY_CONNECTED:
            print("ALREADY_CONNECTED")
        case EduResult.WRONG_CREDENTIALS:
            print("WRONG_CREDENTIALS")
        case EduResult.INVALID_CREDENTIALS:
            print("INVALID_CREDENTIALS")

    skol = Skolengo("here.fr", "here")

    print("Skolengo :")
    match skol.connect_educonnect(edu, "TOULO-EDU_parent_eleve"):
        case Skoresult.ALREADY_CONNECTED:
            print("ALREADY_CONNECTED")
        case Skoresult.EDUCONNECT_NOT_CONNECTED:
            print("EDUCONNECT_NOT_CONNECTED")
        case Skoresult.BAD_PACKET:
            print("BAD_PACKET")
        case Skoresult.UNKNOWN_ERROR:
            print("UNKNOWN_ERROR")
        case Skoresult.SUCCESS:
            print("SUCCESS")

    # Code here
    mailbox = skol.get_service(SkolengoService.MESSAGERIE)
    msg_list = mailbox.get_messages_list()

    print(msg_list)

    print(msg_list[0].get_discussion_list()[0].content_html)

    print(msg_list[12].get_discussion_list()[0].get_attachments())

    contact = mailbox.get_contacts().get_contact("Mes rubriques/TS, classes inversées")
    print(contact)
    
    skol.disconnect()
    edu.disconnect()
