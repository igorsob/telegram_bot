import sqlalchemy as sa
from framework.database import db

metadata = sa.MetaData()


class Field:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Model:

    class Meta:
        pk_field = None
        name = None
        fields = None
        table = None

    @classmethod
    async def create(cls, **kwargs):
        await db.conn.execute(cls.Meta.table.insert().values(**kwargs))
        row = await (
            await db.conn.execute(
                cls.Meta.table.select().order_by(
                    getattr(cls.Meta.table.c, cls.Meta.pk_field).desc()
                ))
        ).first()
        instance = cls()
        for key, value in dict(row).items():
            setattr(instance, key, value)
        return instance

    @classmethod
    async def get(cls, pk):
        row = await (
            await db.conn.execute(
                cls.Meta.table.select().where(
                    getattr(cls.Meta.table.c, cls.Meta.pk_field) == pk
                ))
        ).first()
        instance = cls()
        for key, value in dict(row).items():
            setattr(instance, key, value)
        return instance

    @classmethod
    async def filter_one(cls, **kwargs):
        row = await (
            await db.conn.execute(
                cls.Meta.table.select().where(
                    *[getattr(cls.Meta.table.c, key) == value for key, value in kwargs.items()]
                ))
        ).first()
        if not row:
            return None
        instance = cls()
        for key, value in dict(row).items():
            setattr(instance, key, value)
        return instance

    @classmethod
    async def filter(cls, **kwargs):
        rows = await (await db.conn.execute(
            cls.Meta.table.select().where(
                *[getattr(cls.Meta.table.c, key) == value for key, value in kwargs.items()]
            )
        )).fetchall()
        if not rows:
            return []
        instances = []
        for row in rows:
            instance = cls()
            for key, value in dict(row).items():
                setattr(instance, key, value)
            instances.append(instance)
        return instances

    async def save(self):
        await db.conn.execute(self.Meta.table.update().where(
            getattr(self.Meta.table.c, self.Meta.pk_field) == getattr(self, self.Meta.pk_field)
        ).values({key: getattr(self, key) for key in self.Meta.fields.keys()}))

    async def delete(self):
        await db.conn.execute(self.Meta.table.delete().where(
            getattr(self.Meta.table.c, self.Meta.pk_field) == getattr(self, self.Meta.pk_field)
        ))

    @classmethod
    def init_model(cls):
        cls.Meta.fields = {}
        for key, value in cls.__dict__.items():
            if isinstance(value, Field):
                cls.Meta.fields[key] = sa.Column(key, *value.args, **value.kwargs)
        cls.Meta.table = sa.Table(cls.Meta.name, metadata, *list(cls.Meta.fields.values()))
