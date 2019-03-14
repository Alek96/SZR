from django.conf import settings
from django.db.models.signals import class_prepared
from django.dispatch import receiver


# @receiver(class_prepared)
# def add_db_table_prefix(sender, **kwargs):
#     prefix = getattr(settings, 'DB_TABLE_PREFIX', None)
#     if prefix:
#         # sender._meta.db_table = prefix + sender._meta.db_table
#         print(prefix + sender._meta.db_table)
