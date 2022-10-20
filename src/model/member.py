from datetime import datetime


class Member:
    def __init__(self, member_id: int, username: str, level: int = 0, first_join: datetime = datetime.now(),
                 last_join: datetime = datetime.now(), last_update: datetime = datetime.now(),
                 is_banned: bool = False, member_left: bool = False):
        self._member_id = member_id
        self._username = username
        self._level = level
        self._first_join = first_join
        self._last_join = last_join
        self.last_update = last_update
        self._is_banned = is_banned
        self._member_left = member_left

    @property
    def member_id(self):
        return self._member_id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        if username is not self._username:
            self.last_update = datetime.now()
        self._username = username

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        if level is not self._level:
            self.last_update = datetime.now()
        self._level = level

    @property
    def first_join(self):
        return self._first_join

    @property
    def last_join(self):
        return self._last_join

    @last_join.setter
    def last_join(self, last_join):
        if last_join is not self._last_join:
            self.last_update = datetime.now()
        self._last_join = last_join

    @property
    def is_banned(self):
        return self._is_banned

    @is_banned.setter
    def is_banned(self, is_banned):
        if is_banned is not self.is_banned:
            self.last_update = datetime.now()
        self._is_banned = is_banned

    @property
    def member_left(self):
        return self._member_left

    @member_left.setter
    def member_left(self, member_left):
        if member_left is not self._member_left:
            self.last_update = datetime.now()
        self._member_left = member_left
