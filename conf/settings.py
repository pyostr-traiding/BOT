import ast
import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

class Settings:
    PRODUCTION: bool = ast.literal_eval(os.getenv('PRODUCTION'))
    PATH_MEDIA: str = os.getenv('PATH_MEDIA')

    BASE_API_URL: str = os.getenv('BASE_API_URL')
    AUTH_API_TOKEN: str = os.getenv('AUTH_API_TOKEN')

    BASE_HEADERS = {
        'Authorization': f'Bearer {os.getenv('AUTH_API_TOKEN')}',
    }
    ADMIN_LIST: List[int] = [572982939]

settings = Settings()