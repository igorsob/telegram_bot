from framework.model import Model, Field, sa


class Users(Model):
    id = Field(sa.Integer, primary_key=True)
    t_id = Field(sa.Integer)
    is_bot = Field(sa.Boolean, default=True)
    first_name = Field(sa.String(255), default='')
    last_name = Field(sa.String(255), default='')
    username = Field(sa.String(255), default='')
    language_code = Field(sa.String(255), default='')
    main_message_id = Field(sa.Integer, nullable=True)
    stage = Field(sa.String(255), default='')

    class Meta:
        name = 'users'
        pk_field = 'id'

    @classmethod
    async def create_from_t_user(cls, user, stage=None):
        user = await cls.create(
            t_id=user.id,
            is_bot=user.is_bot,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
            stage=stage
        )
        return user


Users.init_model()
