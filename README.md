# pydantic-computed
A new decorator for pydantic allowing you to define dynamic fields that are computed from other properties.

## Installation

Install the package by running
```bash
pip install pydantic_computed
```

## Examples and use cases


### A computed integer property
```python
from pydantic import BaseModel
from pydantic_computed import Computed, computed

class ComputedModelInt(BaseModel):
    a: int
    b: int
    c: Computed[int]
    @computed('c')
    def calculate_c(a: int, b: int, **kwargs):
        return a + b

model = ComputedModelInt(a=1, b=2)
print(model.c) # Outputs 3
```

### Multiple computed properties

```python
from pydantic import BaseModel
from pydantic_computed import Computed, computed

class MultipleComputed(BaseModel):
    a: int
    b: int
    c: Computed[int]
    d: Computed[int]
    e: Computed[int]
    @computed('c')
    def calc_c(a: int, b: int, **kwargs):
        return a + b

    @computed('d')
    def calc_d(c: int, **kwargs): # Note that property d uses the value of the computed property c (The order of declaration matters!)
        return c * 2

model = MultipleComputed(a=1, b=2)
print(model.c) # Outputs 3
print(model.d) # Outputs 6
```

Since all properties are passed as **kwargs to calculate_c, we can use the property names for the parameters


### Complex types

Suppose you set up a FastAPI application where you have users and orders stored in a database.
All Models in the database have an automatically generated id.
Now you want to be able to dynamically generate links to those objects.
E.g. the user with id=3 is accessible on the endpoint http://my-api/users/3
Instead of storing those links in the database you can simply generate them with the computed decorator.
example: 

```python
from pydantic import BaseModel, Field
from pydantic_computed import Computed, computed

class Link(BaseModel):
    href: str
    method: str

class SchemaLinked(BaseModel):
    id: int
    base_url: str
    link: Computed[Link]
    @computed('link')
    def compute_link( id: int, base_url: str, **kwargs):        
        return Link(href=f'{base_url}/{id}', method='GET')

class User(SchemaLinked):
    base_url: str = Field('/users', exclude=True)
    username: str

class Order(SchemaLinked):
    base_url: str = Field('/orders', exclude=True)
    user: User

user = User(id=3, username='exampleuser') 
user.json()
"""
{
    id: 3,
    username: "exampleuser",
    link: {
        href: "/users/3",
        method: "GET"
    }
}
"""
order = Order(id=2, user=user)
order.json()
"""
{
    id: 2,
    link: {
        href: "/orders/2",
        method: "GET"
    },
    user: {
        id: 3,
        username: "exampleuser",
        link: {
            href: "/users/3",
            method: "GET"
        }
    }
}
"""
``` 


### Vector example:

```python
from pydantic import BaseModel
from pydantic_computed import computed, Computed
import math

class Point(BaseModel):
    x: int
    y: int

class Vector(BaseModel):
    p1: Point
    p2: Point
    x: Computed[float]
    y: Computed[float]
    weight: Computed[float]

    @computed('x')
    def compute_x(p1: Point, p2: Point, **kwargs):
        return p2.x - p1.x
    @computed('y')
    def compute_y(p1: Point, p2: Point, **kwargs):
        return p2.y - p1.y
    @computed('weight')
    def compute_weight(x: float, y: float, **kwargs):
        return math.sqrt(x ** 2 + y ** 2)

v1 = Vector(p1=Point(x=0,y=0), p2=Point(x=1,y=0))
print(v1.weight) # Outputs 1.0
v1.p2 = Point(x=2,y=0)
print(v1.weight) # Outputs now 2.0 since p2 changed
# NOTE: if we would have written v1.p2.x = 2 instead of v1.p2 = Point(x=2, y=0), it would not have worked, because of the way pydantic triggers validations
# The computed field only gets updated if one of the fields in the same model changes (in this case it is property p1 of Vector)
```
