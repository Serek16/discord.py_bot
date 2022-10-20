import datetime
import time

from src.model.member import Member


def updateValueTest():
    # given
    creation_date = datetime.datetime.now()
    member = Member(0, "username", 0, last_update=creation_date)

    # when
    time.sleep(0.05)
    member.level = 5

    # then
    if member.last_update != creation_date:
        print("updateValueTest passed")
    else:
        raise Exception('Member.last_update value was no updated')


if __name__ == '__main__':
    updateValueTest()
