import json

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    status: int
    text: str

    def error_text(self):

        if self.status == 404:
            try:
                text = (
                    'При запросе произошла ошибка\n'
                    f'Статус: {self.status}\n'
                    f'Ошибка: {json.loads(self.text)['msg']}\n'

                )
            except:
                text = (
                    'При запросе произошла ошибка\n'
                    f'Статус: {self.status}\n'
                    f'Ошибка: {self.text}\n'
                )
        else:
            text = (
                'При запросе произошла ошибка\n'
                f'Статус: {self.status}\n'
                f'Ошибка: {self.text}\n'
            )
        return text