from __future__ import annotations
from typing import List, Dict, Optional, Annotated
from pydantic import BaseModel, field_validator, Field
from pydantic.dataclasses import Literal
import re


class Chip(BaseModel):
    code: str
    displayCode: str
    name: str
    display: Display


#----------------------------------------------------------------------------------------------------------------------
Gender = Literal['MEN', 'WOMEN', 'UNISEX']

# "colors": [
#           {
#             "code": "COL00",
#             "displayCode": "00",
#             "name": "WHITE",
#             "display": { "showFlag": true, "chipType": 0 },
#             "filterCode": "WHITE"
#           }
# ]
class Display(BaseModel):
    showFlag: bool
    chipType: int


class Color(Chip):
    filterCode: str


#----------------------------------------------------------------------------------------------------------------------
# "prices": {
#           "base": {
#             "currency": { "code": "USD", "symbol": "$" },
#             "value": 14.9
#           },
#           "promo": {
#             "currency": { "code": "USD", "symbol": "$" },
#             "value": 14.9
#           },
#           "isDualPrice": false
#         },

class Currency(BaseModel):
    code: str
    symbol: str


class PriceBase(BaseModel):
    currency: Currency
    value: float


class PricePromo(BaseModel):
    currency: Currency
    value: float


class Prices(BaseModel):
    base: PriceBase
    promo: PricePromo | None
    isDualPrice: bool


#----------------------------------------------------------------------------------------------------------------------

class Pld(Chip):
    pass


#----------------------------------------------------------------------------------------------------------------------
class Rating(BaseModel):
    average: float
    count: int


#----------------------------------------------------------------------------------------------------------------------
class EffectiveTime(BaseModel):
    start: int
    end: int


class Substitutions(BaseModel):
    flagName: str
    date: str


class NameWording(BaseModel):
    flagWithTime: str
    substitutions: Substitutions


class PriceFlag(BaseModel):
    code: str
    name: str
    id: int
    rank: int
    type: str
    effectiveTime: EffectiveTime
    flagColor: str
    nameWording: NameWording


class Flags(BaseModel):
    priceFlags: List[PriceFlag]
    productFlags: List


class Size(Chip):
    pass


class Representative(BaseModel):
    color: Color
    flags: Flags
    l2Id: str
    pld: Pld
    sales: bool
    size: Size
    communicationCode: str


#----------------------------------------------------------------------------------------------------------------------

class ImageMainItem(BaseModel):
    image: str
    video: Optional[str] = None
    model: List = []

class ImageSubItem(BaseModel):
    image: Optional[str] = None
    video: Optional[str] = None
    model: List = []


#ImageCode: str = Field(pattern=r'^\d{2}$')


class Image(BaseModel):
    main: Dict[str, ImageMainItem]
    chip: Dict[str, str]
    sub: List[ImageSubItem]

    @field_validator('main', 'chip', mode='before')
    def check_keys(cls, values):
        for key in values.keys():
            if not re.fullmatch(r'^\d{2}$', key):
                raise ValueError(f"Invalid key '{key}': must be a two-digit string")
        return values


#----------------------------------------------------------------------------------------------------------------------

class FullUniqloProduct(BaseModel):
    colors: List[Color]
    genderName: Gender
    genderCategory: Gender
    images: Image
    l1Id: str
    name: str
    prices: Prices
    productId: str
    priceGroup: str
    plds: List[Pld]
    rating: Rating
    representative: Representative
    sizes: List[Size]
    promotionText: str
    storeStockOnly: bool


class UniqloProduct(BaseModel):
    colors: List[Color]
    genderName: Gender
    #genderCategory: Gender
    images: Image
    l1Id: str
    name: str
    prices: Prices
    productId: str
    #priceGroup: str
    #plds: List[Pld]
    #rating: Rating
    #representative: Representative
    sizes: List[Size]
    #promotionText: str
    #storeStockOnly: bool
