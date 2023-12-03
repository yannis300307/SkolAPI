import getpass

from educonnect import EduConnect
from skolengo import Skolengo

if __name__ == '__main__':
    edu = EduConnect()

    edu.connect(input("username ? "), getpass.getpass())

    skol = Skolengo("", "")

    skol.connect_educonnect(edu, "TOULO-EDU_parent_eleve")

    # Code here

    skol.disconnect()
    edu.disconnect()


