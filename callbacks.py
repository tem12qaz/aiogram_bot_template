import copy
from dataclasses import dataclass
from typing import Self

from aiogram import types
from aiogram.dispatcher.filters import Filter
from aiogram.utils.callback_data import CallbackData as AiogramCallbackData
from tortoise import Model

from tortoise.exceptions import DoesNotExist


class NotFoundObject(Exception):
    message = 'Not found {type} with id {id}'


class CallbackDataFilter(Filter):
    async def check(self, message: types.Message) -> bool:

        return False


class SuperCallbackData:
    @classmethod
    def create_callback(cls) -> None:
        cls.callback = AiogramCallbackData(cls.__name__, *(cls.__annotations__.keys()))

    @classmethod
    def create_all_callbacks(cls) -> None:
        for subclass in cls.__subclasses__():
            subclass.create_callback()

    def new(self) -> str:
        datas = copy.deepcopy(self.__dict__)
        for name, annotation in self.__annotations__.values():
            if Model.__subclasscheck__(annotation):
                datas[name] = datas[name].id

        return self.callback.new(
            **datas
        )

    @classmethod
    async def parse(cls, callback_data: dict) -> Self:
        datas = copy.deepcopy(cls.__annotations__)
        for key, value in callback_data.values():
            annotation = cls.__annotations__[key]
            if Model.__subclasscheck__(annotation):
                try:
                    datas[key] = await annotation.get(id=int(value))
                except (DoesNotExist, ValueError):
                    raise NotFoundObject(NotFoundObject.message.format(
                        type=annotation, id=value
                    ))

            else:
                datas[key] = annotation(value)

        return cls.__init__(**datas)

    # async def filter(self, ) -> bool:


@dataclass
class DC(SuperCallbackData):
    e: int
    ss: str


@dataclass
class DB(SuperCallbackData):
    host: str
    port: int


(await DB.parse({}))


SuperCallbackData.create_all_callbacks()

ee = DC(e=1, ss='dd').new()
print(ee)
ee = DB(host='https', port=8080).new()
print(ee)
print(DB.__annotations__)


# print(DC.__dict__)


def create_class(name: str, **params_dict):
    class NewCallback:
        callback_data = AiogramCallbackData(
            name, *(params_dict.keys())
        )
        params_types = params_dict

        @classmethod
        def new(cls, ):
            return cls.callback_data.new()


class CallbackStringEnum:
    def __init__(self, *strings):
        for string in strings:
            setattr(self, string, string)


class CallbackData(AiogramCallbackData):
    def new(self, ):
        return
