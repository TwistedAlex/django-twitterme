from django.core import serializers
from utils.json_encoder import JSONEncoder


class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        # Django 的 serializers 默认需要一个 QuerySet 或者 list 类型的数据来进行序列化
        # 因此需要给 instance 加一个 [] 变成 list
        return serializers.serialize('json', [instance], cls=JSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        # 需要加 .object 来得到原始的 model 类型的 object 数据，要不然得到的数据并不是一个
        # ORM 的 object，而是一个 DeserializedObject 的类型
        return list(serializers.deserialize('json', serialized_data))[0].object
