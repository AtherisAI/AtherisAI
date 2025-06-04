import os

class EnvVars:
    @staticmethod
    def get(key: str, default: str = None) -> str:
        value = os.environ.get(key, default)
        print(f"[EnvVars] Retrieved env var: {key} = {value}")
        return value

    @staticmethod
    def require(key: str) -> str:
        value = os.environ.get(key)
        if value is None:
            raise EnvironmentError(f"[EnvVars] Required environment variable '{key}' not found")
        print(f"[EnvVars] Retrieved required env var: {key} = {value}")
        return value

    @staticmethod
    def as_int(key: str, default: int = 0) -> int:
        value = os.environ.get(key)
        try:
            return int(value)
        except (TypeError, ValueError):
            print(f"[EnvVars] Invalid int for {key}, defaulting to {default}")
            return default

    @staticmethod
    def as_bool(key: str, default: bool = False) -> bool:
        value = os.environ.get(key)
        if value is None:
            return default
        return value.lower() in ("1", "true", "yes")


# Example usage
if __name__ == "__main__":
    os.environ["ATHERIS_ENV"] = "production"
    os.environ["DASHBOARD_PORT"] = "8080"
    os.environ["USE_SSL"] = "true"

    env = EnvVars()
    print(env.get("ATHERIS_ENV"))
    print(env.require("DASHBOARD_PORT"))
    print(env.as_int("DASHBOARD_PORT"))
    print(env.as_bool("USE_SSL"))
    print(env.as_bool("DEBUG", default=True))
