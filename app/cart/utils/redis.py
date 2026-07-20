class CartRedis:
    @classmethod
    def key(cls, user_id: str) -> str:
        return f"cart:{user_id}"
