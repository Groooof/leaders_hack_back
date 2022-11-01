import pydantic as pd
import datetime as dt
import re
import typing as tp
from enum import Enum


def validate_phone(phone):
    """
    Валидация номера телефона.
    """
    regex = '^7[0-9]{10}$'
    if not re.search(regex, phone):
        raise ValueError('Wrong phone format')
    return phone


class CreditPurposes(str, Enum):
    """
    Цели оформления кредита.
    """
    flat = 'flat'
    other = 'other'


class RequestUserData(pd.BaseModel):
    """
    Входные данные от пользователя для обработки.
    """
    surname: str
    name: str
    patronymic: str
    phone: str
    birthday: dt.date
    document_type: str
    passport_series: str = pd.Field(min_length=4, max_length=4)
    passport_number: str = pd.Field(min_length=6, max_length=6)
    profit: int
    amount: int
    benefits: bool
    purpose: CreditPurposes

    _phone_validator = pd.validator('phone')(validate_phone)

    class Config:
        schema_extra = {
            'example': {
                'surname': 'Ермаков',
                'name': 'Максим',
                'patronymic': 'Владимирович',
                'phone': '79780000009',
                'birthday': '1998-06-30',
                'document_type': 'паспорт',
                'passport_series': '0009',
                'passport_number': '000009',
                'profit': '70000',
                'amount': '100000',
                'benefits': 'True',
                'purpose': 'other'
            }
        }


class AvailableCreditInfo(pd.BaseModel):
    """
    Возвращаемая информация о найденном доступном кредитном продукте
    """
    name: str
    monthly_payment: tp.Optional[int]
    period: tp.Optional[int]
    overpayment: tp.Optional[int]
    interest_rate: tp.Optional[float]


class ResponseAvailableCreditProducts(pd.BaseModel):
    """
    Возвращаемая информация о найденных доступных кредитных продуктах
    """
    min_overpayment: tp.List[AvailableCreditInfo] = pd.Field(default_factory=list)
    min_monthly_payment: tp.List[AvailableCreditInfo] = pd.Field(default_factory=list)

