import os
import turso_serverless

def get_db():
    return turso_serverless.connect(
        os.environ["TURSO_DATABASE_URL"],
        auth_token=os.environ["TURSO_AUTH_TOKEN"]
    )
