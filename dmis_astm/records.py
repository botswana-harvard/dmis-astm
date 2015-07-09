# # import pyodbc
# 
# from django.conf import settings
# 
# # from getresults.models import Panel, Utestid
# 
# DNS = ('DRIVER=/usr/local/lib/libtdsodbc.so;SERVER=192.168.1.10;PORT=1433;UID=sa;PWD=cc3721b;DATABASE=BHPLAB')
# 
# 
# # class Records(object):
# # 
# #     item_cls = None
# # 
# #     def __init__(self, identifier):
# #         self.values = []
# #         self.identifier = identifier
# #         with pyodbc.connect(DNS) as cnxn:
# #             with cnxn.cursor() as cursor:
# #                 for row in cursor.execute(self.sql).fetchall():
# #                     self.values.append(self.item_cls(*row))
# # 
# #     def __iter__(self):
# #         for values in self.values:
# #             yield values
# # 
# #     @property
# #     def sql(self):
# #         return None
# 
# 
# class Order(object):
# 
#     def __init__(self, order_identifier, order_datetime):
#         self.order_identifier = order_identifier
#         self.order_datetime = order_datetime
# 
# 
# class Result(object):
# 
#     def __init__(
#             self, result_identifier, result_datetime, utestid_name, result_value, result_quantifier,
#             assay_datetime):
#         self.result_identifier = result_identifier
#         self.result_datetime = result_datetime
#         # self.panel = Panel.objects.get(name=panel_name)
#         self.result_value = result_value
#         self.result_quantifier = result_quantifier
#         self.assay_datetime = assay_datetime
#         self.utestid = Utestid.objects.get(name=utestid_name)
# 
# 
# class Orders(Records):
# 
#     item_cls = Order
# 
#     @property
#     def sql(self):
#         return str(
#             'select l21.pid as order_identifier, l21.headerdate as order_datetime '
#             'from bhplab.dbo.lab21response as l21 '
#             'left join bhplab.dbo.lab01response as l on l21.pid=l.pid '
#             'where l21.pid=\'{}\'').format(self.identifier)
# 
# 
# class ResultItems(Records):
# 
#     item_cls = ResultItem
# 
#     @property
#     def sql(self):
#         return str('SELECT * from LAB21Response where result_guid=\'{}\'')
# 
# 
# class Results(Records):
# 
#     item_cls = Result
# 
#     @property
#     def sql(self):
#         return str(
#             'select l21.pid as order_identifier, l21.headerdate as order_datetime '
#             'from bhplab.dbo.lab21response as l21 '
#             'left join bhplab.dbo.lab01response as l on l21.pid=l.pid '
#             'where l21.pid=\'{}\'').format(self.aliquot_identifier)
#     