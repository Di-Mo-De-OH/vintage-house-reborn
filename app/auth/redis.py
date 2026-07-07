class EmailRedis:
    @classmethod
    def code(cls,email:str)->str:
        return f"email:code:{email}"

    @classmethod
    def verify(cls,token:str)->str:
        return f"email:verify:{token}"