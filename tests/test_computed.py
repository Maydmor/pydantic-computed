import math

from pydantic import VERSION

if VERSION.startswith("2."):
    from pydantic.v1 import BaseModel
else:
    from pydantic import BaseModel


from pydantic_computed import Computed, computed


class ComputedModelInt(BaseModel):
    a: int
    b: int
    c: Computed[int]

    @computed("c")
    def calculate_c(a: int, b: int, **kwargs):
        return a + b


class ComputedModelStr(BaseModel):
    a: int
    b: int
    c: Computed[str]

    @computed("c")
    def calculate_c(a: int, b: int, **kwargs) -> str:
        return str(a + b)


class ComputedModelKwargs(BaseModel):
    a: int
    b: int

    c: Computed[str]

    @computed("c")
    def calculate_c(a: int, **kwargs) -> str:
        return str(kwargs.get("b") * a)


class ComputedModelNoArgs(BaseModel):
    a: int
    b: int
    c: Computed[int]

    @computed("c")
    def calculate_c(**kwargs):
        return 5


class MultipleComputed(BaseModel):
    a: int
    b: int
    c: Computed[int]
    d: Computed[int]
    e: Computed[int]

    @computed("c")
    def calc_c(a: int, b: int, **kwargs):
        print(a)
        return a + b

    @computed("d")
    def calc_d(c: int, **kwargs):
        return c * 2


class Point(BaseModel):
    class Config:
        copy_on_model_validation = "deep"

    x: int
    y: int


class Vector(BaseModel):
    class Config:
        copy_on_model_validation = "deep"

    p1: Point
    p2: Point
    x: Computed[float]
    y: Computed[float]
    weight: Computed[float]

    @computed("x")
    def compute_x(p1: Point, p2: Point):
        return p2.x - p1.x

    @computed("y")
    def compute_y(p1: Point, p2: Point):
        return p2.y - p1.y

    @computed("weight")
    def compute_weight(x: float, y: float, **kwargs):
        return math.sqrt(x**2 + y**2)


class Triangle(BaseModel):
    class Config:
        copy_on_model_validation = "deep"

    a: Vector
    b: Vector
    c: Vector
    area: Computed[float]

    @computed("area")
    def compute_area(a: Vector, b: Vector, c: Vector, **kwargs):
        l1, l2, l3 = a.weight, b.weight, c.weight
        s = (l1 + l2 + l3) / 2
        return math.sqrt(s * (s - l1) * (s - l2) * (s - l3))


def test_simple():
    model = ComputedModelInt(a=1, b=2)
    assert model.c == 3


def test_to_dict():
    model = ComputedModelInt(a=1, b=2)
    assert model.dict().get("c") == 3


def test_to_json():
    model = ComputedModelInt(a=1, b=2)
    assert model.json().find("c") != -1


def test_overwrites_value():
    model = ComputedModelInt(a=1, b=2, c=5)
    assert model.c == 3


def test_datatype_conversion():
    model = ComputedModelStr(a=1, b=2)
    assert model.c == "3"


def test_property_change():
    model = ComputedModelInt(a=1, b=2)
    model.c = 3
    model.a = 2
    model.b = 3
    assert model.c == 5


def test_use_kwargs():
    model = ComputedModelKwargs(a=2, b=3)
    assert model.c == "6"


def test_no_parameters():
    model = ComputedModelNoArgs(a=1, b=2)
    assert model.c == 5


def test_multiple_computed():
    model = MultipleComputed(a=1, b=2)
    assert model.d == 6


def test_multimodel():
    p1 = Point(x=0, y=0)
    p2 = Point(x=0, y=1)
    p3 = Point(x=1, y=0)
    v1 = Vector(p1=p1, p2=p2)
    v2 = Vector(p1=p2, p2=p3)  # Hypotenuse
    v3 = Vector(p1=p1, p2=p3)
    assert v1.weight == 1
    assert v3.weight == 1
    assert abs(v2.weight**2 - (v1.weight**2 + v3.weight**2)) < 0.01
    s = (1 + 1 + 1) / 2
    t = Triangle(a=v1, b=v2, c=v3)
    assert abs(t.area - 1 / 2) < 0.01
