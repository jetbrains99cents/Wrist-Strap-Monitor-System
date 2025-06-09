# File: app/schemas/pyobjectid.py

from bson import ObjectId
from typing import Any, Callable

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        def validate_from_object_id(value: ObjectId) -> str:
            return str(value)

        from_object_id_schema = core_schema.chain_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(validate_from_object_id),
            ]
        )

        return core_schema.union_schema(
            [
                from_object_id_schema,
                core_schema.str_schema(),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )