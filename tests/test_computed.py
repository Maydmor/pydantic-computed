import pytest
from pydantic import BaseModel
from pydantic_computed import Computed, computed

class ComputedModelInt(BaseModel):
    a: int
    b: int
    c: Computed[int]
    @computed('c')
    def calculate_c(a: int, b: int):
        return a + b

class ComputedModelStr(BaseModel):
    a: int
    b: int
    c: Computed[str]
    @computed('c')
    def calculate_c(a: int, b: int):
        return a + b
    
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
    