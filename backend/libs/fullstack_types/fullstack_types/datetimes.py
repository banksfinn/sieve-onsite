from typing import Annotated

from arrow import Arrow, get
from pydantic import PlainSerializer, PlainValidator, WithJsonSchema

AnnotatedArrow = Annotated[
    Arrow,
    PlainValidator(lambda x: get(x)),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="validation"),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
