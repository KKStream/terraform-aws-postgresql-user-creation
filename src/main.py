import json
import logging
import os

import boto3

import psycopg2


def handler(event, context):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    
    master_arn = os.getenv('SECRETS_RDS_MASTER_ARN')
    user_arn = os.getenv('SECRETS_RDS_USER_ARN')

    client = boto3.client('secretsmanager')
    master = json.loads(client.get_secret_value(SecretId=master_arn).get('SecretString'))
    user = json.loads(client.get_secret_value(SecretId=user_arn).get('SecretString'))
    logger.info(f'Get user information.')

    endpoint = event.get("DB_ENDPOINT")
    db_name = event.get("DB_NAME")
    port = event.get("DB_PORT")

    conn_str = f'host={endpoint} ' \
               f'port={port} ' \
               f'user={master["username"]} ' \
               f'password={master["password"]} ' \
               f'dbname={db_name}'

    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute(f"""SELECT 1 FROM pg_roles WHERE rolname='{user["username"]}'""")
    rs = cursor.fetchall()

    if rs:
        logger.info(f'User: {user["username"]} is exists.')
        return

    logger.info(f'Creating user "{user["username"]}".')
    cursor.execute(f"""
        CREATE USER {user["username"]} WITH LOGIN PASSWORD '{user["password"]}';
        GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {user["username"]};
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {user["username"]};
        GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO {user["username"]};
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {user["username"]};
    """)
    conn.commit()
    logger.info(f'User "{user["username"]}" created successfully.')

    conn_str = f'host={endpoint} ' \
               f'port={port} ' \
               f'user={user["username"]} ' \
               f'password={user["password"]} ' \
               f'dbname={db_name}'
    psycopg2.connect(conn_str)
    logger.info(f'User "{user["username"]}" login successfully.')
