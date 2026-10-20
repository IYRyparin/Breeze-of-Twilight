import gc


def get_object_by_id(obj_id):
    for obj in gc.get_objects():
        if id(obj) == obj_id:
            return obj
    return None
