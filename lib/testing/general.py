def dummy(kdict, name='dummy'):
    return type(name, (object,), kdict)()
