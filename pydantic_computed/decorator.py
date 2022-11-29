from pydantic import validator
from typing import Callable, Dict

def computed(property_key: str):
    def __computed_wrapper(method: Callable):
        def __method_wrapper(cls, v, values: Dict):
            """pydantics "validator" wrapper calls the given method with cls, v, and the dict containing the models values,
            for ease of use get rid of cls and v and simply pass the dict of values to the wrapped function"""
            return method(**values)
        return validator(property_key, pre=True, always=True, allow_reuse=True)(__method_wrapper)
    return __computed_wrapper