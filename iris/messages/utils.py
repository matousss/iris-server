from .models import Channel, DirectChannel, GroupChannel


def has_view_perms(user, channel: Channel):
    return channel.users.contains(user)


def has_edit_perms(user, channel: Channel):
    if not has_view_perms(user, channel):
        return False

    if isinstance(channel, DirectChannel) or (isinstance(channel, GroupChannel) and channel.admins.contains(user)):
        return True

    return False
