import os

def save_module(spec, name, location):
    """Create a module on the file system from a spec

    Parameters
    ----------
    spec : dict
        A nested dict specifying the contents of a module
    name : string
        The name of the module, i.e. the name of the directory that will be
        created at ``location``.
    location : string
        A valid file path at which the module source tree will be saved.

    Returns
    -------
    module_path : string
        The path to the resulting module
    """
    if not os.path.isdir(location):
        raise ValueError(f"{location} is not a valid directory")

    module_path = os.path.join(location, name)
    os.mkdir(module_path)
    for filename, contents in spec.items():
        if isinstance(contents, str):
            with open(os.path.join(module_path, filename), 'w') as f:
                f.write(contents)
        elif isinstance(contents, dict):
            save_module(contents, name=filename, location=module_path)
        else:
            raise ValueError("spec values should be either string or dict; "
                             f"got {type(contents)}")
    return module_path
