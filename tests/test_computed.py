import pytest
from pydantic import BaseModel
from pydantic_computed import Computed, computed

class ComputedModelInt(BaseModel):
    a: int
    b: int
    c: Computed[int]
    @computed('c')
    def calculate_c(a: int, b: int):
        print(f'calculate c {a}, {b}')
        return a + b

class ComputedModelStr(BaseModel):
    a: int
    b: int
    c: Computed[str]
    @computed('c')
    def calculate_c(a: int, b: int, **kwargs)->str:
        return str(a + b)

class ComputedModelKwargs(BaseModel):
    a: int
    b: int 

    c: Computed[str]
    @computed('c')
    def calculate_c(a:int, **kwargs):
        return kwargs.get('b') * a
    

class ComputedModelNoArgs(BaseModel):
    a: int
    b: int
    c: Computed[int]
    @computed('c')
    def calculate_c():
        return 5


class MultipleComputed(BaseModel):
    a: int
    b: int
    c: Computed[int]
    d: Computed[int]
    e: Computed[int]
    @computed('c')
    def calc_c(a: int, b: int):
        print(a)
        return a + b

    @computed('d', pre=False)
    def calc_d(c: int):
        return c * 2

def test_simple():
    model = ComputedModelInt(a=1, b=2)
    assert model.c == 3

def test_to_dict():
    model = ComputedModelInt(a=1, b=2)
    assert model.dict().get('c') == 3

def test_to_json():
    model = ComputedModelInt(a=1, b=2)
    assert model.json().find('c') != -1

def test_overwrites_value():
    model = ComputedModelInt(a=1, b=2, c=5)
    assert model.c == 3

def test_datatype_conversion():
    model = ComputedModelStr(a=1, b=2)
    assert model.c == '3'

def test_property_change():
    model = ComputedModelInt(a = 1, b = 2)
    model.c = 3
    model.a = 2
    model.b = 3
    assert model.c == 5

def test_use_kwargs():
    model = ComputedModelKwargs(a=2, b=3)
    assert model.c == '6'

def test_no_parameters():
    model = ComputedModelNoArgs(a = 1, b = 2)
    assert model.c == 5

def test_multiple_computed():
    model = MultipleComputed(a=1, b=2)
    assert model.d == 6