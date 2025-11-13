from pydantic import BaseModel

class AlphaSchema(BaseModel):
    date_open: str = '12.02.2024'
    report_date: str
    client: str = 'Островский Сергей Андреевич'
    address: str = '454090, Россия, г. Челябинск, \nул. Свободы, д. 77, кв. 12'

class TinkSchema(BaseModel):
    date: str = '10.10.2000'
    fio: str = 'Островский Сергей Андреевич'
    series: str = '4020'
    number: str = '700130'
    date_issue: str = '21.03.2015'
    code: str = '780-642'
    issued_by: str = 'ОУФМС России по Челябинской обл. в г. Челябинске'
    address: str = '454090, Россия, г. Челябинск, ул. Свободы, д. 77, кв. 12'
    contract_date: str = '10.02.2024'
    contract_number: str = 'ТИНК-0014578'
    card_number: str = '0011'

class DataSchema(BaseModel):
    alpha: AlphaSchema
    tink: TinkSchema
