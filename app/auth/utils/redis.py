class EmailRedis:
    @classmethod
    def code(cls, email: str) -> str:
        return f"email:code:{email}"

    @classmethod
    def verify(cls, token: str) -> str:
        return f"email:verify:{token}"

    @classmethod
    def cooldown(cls, email: str) -> str:
        return f"email:cooldown:{email}"


class LogoutRedis:
    @classmethod
    def blacklist(cls, jwi: str) -> str:
        return f"access:blacklist:{jwi}"
