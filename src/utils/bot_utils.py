import discord


def has_role(member: discord.Member, role_id: int) -> bool:
    """Check if member has a specific role"""
    
    for role in member.roles:
        if role.id == role_id:
            return True
    return False
