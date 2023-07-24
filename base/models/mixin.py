from sqlalchemy import Column, DateTime, func


class MixinBase:
    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MixinDate:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
