import os
import importlib

def run_async(func):
    '''
    Function decorater to make methods run in a thread
    '''
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func

def attach_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator

import importlib.util

def load_and_assign_functions(directory, cls):
    def assign_to_class(func):
        setattr(cls, func.__name__, func)
    
    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            module_name = filename[:-3]
            file_path = os.path.join(directory, filename)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for name, value in module.__dict__.items():
                if callable(value) and not name.startswith("__"):
                    assign_to_class(value)
