class SQLValidator:
    FORBIDDEN_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"}

    @classmethod
    def validate(cls, sql):
        for kw in cls.FORBIDDEN_KEYWORDS:
            if kw in sql:
                raise ValueError(f"Generated SQL cannot contain {kw} keyword!")
