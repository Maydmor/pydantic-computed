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

class ExampleModel(BaseModel):
    a: int
    b: int
    c: Computed[int]

    @computed('c')
    def calculate_c(a: int, **kwargs):
        return a + 1

model = ExampleModel(a=1, b=2)
print(model.c) # Outputs 2
```

### Multiple properties as parameters

```python
from pydantic import BaseModel
from pydantic_computed import Computed, computed

class ExampleModel(BaseModel):
    a: int
    b: int
    c: Computed[int]

    @computed('c')
    def calculate_c(a: int, b: int):
        return a + 1

model = ExampleModel(a=1, b=2)
print(model.c) # Outputs 2
```

Since all properties are passed as **kwargs to calculate_c, we can use the property names for the parameters

### Automatic type conversion

```python
from pydantic import BaseModel
from pydantic_computed import Computed, computed

from pydantic import BaseModel
from pydantic_computed import Computed, computed

class ExampleModel(BaseModel):
    a: int
    b: int
    c: Computed[str]

    @computed('c')
    def calculate_c(a: int, b: int):
        return a + b

model = ExampleModel(a=1, b=2)
print(model.c) # Outputs '3' as string
```

Automatic type conversion happens for the returned value

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
    def compute_link( id: int, base_url: str):        
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
