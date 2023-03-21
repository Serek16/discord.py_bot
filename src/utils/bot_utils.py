import discord


def has_role(member: discord.Member, role_id: int) -> bool:
    """Check if member has a specific role"""

    for role in member.roles:
        if role.id == role_id:
            return True
    return False


def extract_channel_id(channel: str) -> int:
    """Extract channel id from channel tag. It can have format e.g. "<#964219276145852530>" or "964219276145852530".
    Otherwise, ValueError exception is raised."""

    if channel.startswith("<#") and channel.endswith('>'):
        return int(channel[2:-1])

    try:
        return int(channel)
    except ValueError:
        raise ValueError(f"Couldn't extract channel id from \"{channel}\"")


def extract_user_id(user: str) -> int:
    """Extract user id from user tag. It can have format e.g. "<@972860635933179915>" or "972860635933179915".
    Otherwise, ValueError exception is raised."""

    if user.startswith('<@') and user.endswith('>'):
        return int(user[2:-1])

    try:
        return int(user)
    except ValueError:
        raise ValueError(f"Couldn't extract channel id from \"{user}\"")
