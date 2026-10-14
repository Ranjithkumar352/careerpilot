def select_role(user_message, suggested_roles):

    user_message = user_message.strip().lower()

    for role in suggested_roles:

        role_name = role["role"].strip().lower()

        if user_message == role_name:
            return role["role"]

    # Allow the user to type a role that wasn't displayed
    for role in suggested_roles:

        role_name = role["role"].strip().lower()

        if role_name in user_message:
            return role["role"]

    # If user directly types another role
    if len(user_message) >= 3:
        return user_message.strip()

    return None