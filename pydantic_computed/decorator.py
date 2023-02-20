from pydantic import validator, root_validator, create_model
from typing import Callable, Dict
from inspect import getargspec, signature

COMPUTED_FIELDS = {}

def get_parameters(method, values, property_key):
    method_params = signature(method).parameters
    parameter_names = [name for name,param in method_params.items() if param.kind == param.POSITIONAL_OR_KEYWORD]
    parameters = {property: values[property] for property in parameter_names if property != property_key}
    # create the dictionary containing all remaining unnamed/kwarg parameters
    new_kwarg_names = list(filter(lambda key: key not in parameters, values.keys()))
    new_kwargs = {property: values[property] for property in new_kwarg_names if property != property_key}
    # pass in var keyword arguments if function has e.g. **kwargs in signature
    contains_var_keyword_arg = lambda params: len(list(filter(lambda param: param.kind == param.VAR_KEYWORD, params))) > 0
    method_args = dict(new_kwargs, **parameters) if contains_var_keyword_arg(method_params.values()) else parameters
    return method_args

def computed(property_key: str):
    def __wrapper(method: classmethod):
        global COMPUTED_FIELDS
        qualified_class_name = '.'.join(method.__qualname__.split('.')[:-1])        
        def compute(cls, values):
            cls.Config.validate_assignment = True
            for prop_key,computed_method in COMPUTED_FIELDS[qualified_class_name].items():
                parameters = get_parameters(computed_method, values, prop_key)
                values[prop_key] = computed_method(**parameters)
            values[property_key] = COMPUTED_FIELDS[qualified_class_name][property_key](**values)
            return values
        if COMPUTED_FIELDS.get(qualified_class_name) is None:
            COMPUTED_FIELDS[qualified_class_name] = {}
        COMPUTED_FIELDS[qualified_class_name][property_key] = method
        return root_validator(allow_reuse=True)(compute)
    return __wrapper
