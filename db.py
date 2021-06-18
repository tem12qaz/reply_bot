from config import database_uri
from tortoise import Tortoise, fields, Model

TORTOISE_ORM = {
    "connections": {"default": database_uri},
    "apps": {
        "models": {
            "models": ["db", "aerich.models"],
            " default_connection ": "default",
        },
    },
}


async def db_init():
    await Tortoise.init(
        db_url=database_uri,
        modules={'models': ['db']}
    )
    await Tortoise.generate_schemas()


class Url(Model):
    id = fields.IntField(pk=True)
    url = fields.BigIntField(unique=True)
