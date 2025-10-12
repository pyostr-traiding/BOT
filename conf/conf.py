from typing import List

import boto3
import ast
import os
import redis

from dotenv import load_dotenv

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import Redis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage


load_dotenv()



s_redis = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    password=os.getenv('REDIS_PASSWORD'),
    db=3,
)

s_storage = Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD'),
    db=4,
)

s_redis_chat = Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD'),
    db=5,
)


storage = RedisStorage(redis=s_storage)
dp = Dispatcher(storage=storage)
client = Bot(
    token=os.getenv('BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode='HTML'),
)


s3_client = boto3.resource(
    service_name='s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    endpoint_url='https://s3.timeweb.cloud',

)


async def s3_upload(file_name, user_id, path_media='media/', path_s3='bot/media/receipt/'):
    s3_client.Bucket(os.getenv('AWS_STORAGE_BUCKET_NAME')). \
        upload_file(f'{path_media}{file_name}',
                    f'{path_s3}{file_name}',
                    )
    os.remove(f'media/{file_name}')
