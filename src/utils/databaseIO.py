import psycopg2

from src.model.member import Member
from src.utils.bot_utils import get_postgres_credentials
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


def get_all_members() -> list[Member]:
    user_list = []

    conn = None
    try:
        db_params = get_postgres_credentials()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        cur.execute(
            "select member_id, username, level, first_join, last_join, last_update, is_banned, member_left from member")

        row = cur.fetchone()
        while row is not None:
            member_id = row[0]
            username = row[1]
            level = row[2]
            first_join = row[3]
            last_join = row[4]
            last_update = row[5]
            is_banned = row[6]
            member_left = row[7]

            user_list.append(
                Member(member_id, username, level, first_join, last_join, last_update, is_banned, member_left))

            row = cur.fetchone()

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()

    return user_list


def get_member_by_id(member_id: int) -> Member | None:
    member = None

    conn = None
    try:
        db_params = get_postgres_credentials()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        member = cur.execute("select * from member where member_id = %s", (member_id,))
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()

    return member


def save_member(member: Member):
    member_id = member.member_id
    username = member.username
    level = member.level
    first_join = member.first_join
    last_join = member.last_join
    last_update = member.last_update
    is_banned = member.is_banned
    member_left = member.member_left

    conn = None
    try:
        db_params = get_postgres_credentials()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        cur.execute("select * from member where member_id = %s", (member_id,))
        user = cur.fetchone()

        if user is None:
            cur.execute(
                "insert into member "
                "(member_id, username, level, first_join, last_join, last_update, is_banned, member_left)"
                "values(%s, %s, %s, %s, %s, %s, %s, %s)",
                (member_id, username, level, first_join, last_join, last_update, is_banned, member_left))

        else:
            cur.execute(
                "update member set level = %s, last_join = %s, last_update = %s, is_banned = %s, member_left = %s",
                (level, last_join, last_update, is_banned, member_left))

        cur.close()
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
