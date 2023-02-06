from pydantic import validator, root_validator
from typing import Callable, Dict
from inspect import getargspec, signature

def computed(property_key: str, recompute_always: bool = True):
    def __computed_wrapper(method: Callable):
        def __compute_once_method_wrapper(cls, v, values: Dict):
            """
            this wrapper will only be called when recompute_always is set to False. It can be used to save computation time, since it only 
            computes the value when the pydantic object is instantiated.

            pydantics "validator" wrapper calls the given method with cls, v, and the dict containing the models values,
            for ease of use get rid of cls and v and simply pass the dict of values to the wrapped function.
            """
            return method(**values)
        def __method_wrapper(cls, values):
            """ This wrapper is the default method that gets called. It is called whenever any property in the model changes and therefore
            always recomputes the property.
            """
            cls.Config.validate_assignment = True # Rerun code on every assignment operation of any property
            method_params = signature(method).parameters
            # create the dictionary containing all named parameters of the compute method e.g. def calculate_c(a: int, b: int, **kwargs) -> {a, b} 
            parameter_names = [name for name,param in method_params.items() if param.kind == param.POSITIONAL_OR_KEYWORD]
            parameters = {property: values[property] for property in parameter_names}
            # create the dictionary containing all remaining unnamed/kwarg parameters
            new_kwarg_names = list(filter(lambda key: key not in parameters, values.keys()))
            new_kwargs = {property: values[property] for property in new_kwarg_names if property != property_key}
            # pass in var keyword arguments if function has e.g. **kwargs in signature
            contains_var_keyword_arg = lambda params: len(list(filter(lambda param: param.kind == param.VAR_KEYWORD, params))) > 0
            method_args = dict(new_kwargs, **parameters) if contains_var_keyword_arg(method_params.values()) else parameters
            # overwrite value of computed property with method output
            values[property_key] = method(**method_args)
            return values
        if recompute_always:
            return root_validator(allow_reuse=True, pre=True)(__method_wrapper)
        else:
            return validator(property_key, pre=True, allow_reuse=True, always=True)(__compute_once_method_wrapper)
    return __computed_wrapper