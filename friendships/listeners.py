def friendship_changed(sender, instance, **kwargs):
    # import 写在函数里面避免循环依赖
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)
