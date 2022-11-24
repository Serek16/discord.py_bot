def has_role(member, role_id):
    for role in member.roles:
        if role.id == role_id:
            return True
    return False
