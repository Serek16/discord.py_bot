import discord
import psycopg2

from src.model.member import Member
from src.utils.config_val_io import GlobalValues
from src.utils.logger import get_logger

logger = get_logger(__name__, __name__)


def get_all_members() -> list[Member]:
    user_list = []

    conn, cur = __open_db_connection()

    cur.execute(
        "SELECT member_id, username, level, first_join, last_join, last_update, is_banned, member_left FROM member")

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

    __commit_and_close_db_connection(conn, cur)

    return user_list


def get_member_by_id(member_id: int) -> Member | None:
    conn, cur = __open_db_connection()

    cur.execute(
        "SELECT member_id, username, level, first_join, last_join, last_update, is_banned, member_left FROM member "
        "WHERE member_id = %s", (member_id,))
    result = cur.fetchone()

    if result is None:
        return None

    member = Member(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])

    __commit_and_close_db_connection(conn, cur)

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

    conn, cur = __open_db_connection()

    cur.execute("select * from member where member_id = %s", (member_id,))
    user = cur.fetchone()

    if user is None:
        cur.execute(
            "INSERT INTO MEMBER"
            " (member_id, username, level, first_join, last_join, last_update, is_banned, member_left)"
            " VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
            (member_id, username, level, first_join, last_join, last_update, is_banned, member_left))

    else:
        cur.execute(
            "UPDATE member SET"
            " level = %s, first_join = %s, last_join = %s, last_update = %s, is_banned = %s, member_left = %s"
            " WHERE member_id = %s",
            (level, first_join, last_join, last_update, is_banned, member_left, member_id))

    __commit_and_close_db_connection(conn, cur)


def add_upvote(member: discord.Member):
    conn, cur = __open_db_connection()

    cur.execute("SELECT upvotes FROM reactions WHERE member_id = %s", (member.id,))
    reactions = cur.fetchone()

    if reactions is not None:
        upvotes = reactions[0] + 1
        cur.execute("UPDATE reactions SET upvotes = %s WHERE member_id = %s", (upvotes, member.id))
    else:
        cur.execute("INSERT INTO reactions (member_id, username, upvotes, downvotes) VALUES (%s, %s, 1, 0)",
                    (member.id, member.name))

    __commit_and_close_db_connection(conn, cur)


def add_downvote(member: discord.Member):
    conn, cur = __open_db_connection()

    cur.execute("SELECT downvotes FROM reactions WHERE member_id = %s", (member.id,))
    reactions = cur.fetchone()

    if reactions is not None:
        downvotes = reactions[0] + 1
        cur.execute("UPDATE reactions SET downvotes = %s WHERE member_id = %s", (downvotes, member.id))
    else:
        cur.execute("INSERT INTO reactions (member_id, username, upvotes, downvotes) VALUES (%s, %s, 0, 1)",
                    (member.id, member.name))

    __commit_and_close_db_connection(conn, cur)


def remove_upvote(member: discord.Member):
    conn, cur = __open_db_connection()

    cur.execute("SELECT upvotes FROM reactions WHERE member_id = %s", (member.id,))
    reactions = cur.fetchone()

    if reactions is not None:
        upvotes = reactions[0] - 1
        if upvotes <= 0:
            upvotes = 0
        cur.execute("UPDATE reactions SET upvotes = %s WHERE member_id = %s", (upvotes, member.id))
    else:
        cur.execute("INSERT INTO reactions (member_id, username, upvotes, downvotes) VALUES (%s, %s, 0, 0)",
                    (member.id, member.name))

    __commit_and_close_db_connection(conn, cur)


def remove_downvote(member: discord.Member):
    conn, cur = __open_db_connection()

    cur.execute("SELECT downvotes FROM reactions WHERE member_id = %s", (member.id,))
    reactions = cur.fetchone()

    if reactions is not None:
        downvotes = reactions[0] - 1
        if downvotes <= 0:
            downvotes = 0
        cur.execute("UPDATE reactions SET downvotes = %s WHERE member_id = %s", (downvotes, member.id))
    else:
        cur.execute("INSERT INTO reactions (member_id, username, upvotes, downvotes) VALUES (%s, %s, 0, 0)",
                    (member.id, member.name))

    __commit_and_close_db_connection(conn, cur)


def get_reaction_list(reaction_num: int) -> list[dict]:
    conn, cur = __open_db_connection()

    cur.execute("SELECT * FROM reactions ORDER BY upvotes DESC LIMIT %s", (reaction_num,))
    r = cur.fetchall()

    result = []
    for reaction in r:
        result.append({
            "member_id": reaction[0],
            "upvotes": reaction[1],
            "downvotes": reaction[2]
        })

    __commit_and_close_db_connection(conn, cur)

    return result


def __open_db_connection():
    conn = None
    try:
        db_params = GlobalValues.get('postgres')
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        return conn, cur

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        if conn is not None:
            conn.close()


def __commit_and_close_db_connection(conn, cur):
    try:
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)

    finally:
        if conn is not None:
            conn.close()
