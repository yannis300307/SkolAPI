import getpass


if __name__ == '__main__':
    edu = EduConnect()
    edu.connect(input("username ? "), getpass.getpass())
