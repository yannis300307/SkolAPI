import getpass

from educonnect import EduConnect

if __name__ == '__main__':
    edu = EduConnect()
    print(edu.is_account_connected())
    edu.connect(input("username ? "), getpass.getpass())
    print(edu.is_account_connected())
