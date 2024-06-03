# import aiogram
# import aiogram.filters as aiogram_filters
#
# import lib.app.split_settings as app_split_settings
# import lib.structures.collections as structures_states
#
#
# class IsAdminFilter(aiogram_filters.BaseFilter):
#     def __init__(
#         self,
#         settings: app_split_settings.AppSettings,
#         admin_collection: structures_states.Collection,
#     ):
#         self.settings = settings
#         self.admin_collection = admin_collection
#
#     async def __call__(self, message: aiogram.types.Message) -> bool:
#         if not message.from_user:
#             return False
#
#         user_id = message.from_user.id
#         is_admin = await self.admin_collection.check_value(str(user_id))
#
#         return is_admin or (user_id in self.settings.admin_ids)
