from django.conf import settings
from django.utils.encoding import force_str


def get_key(model):
    """
    Get key of the model.

    By default returns 'pk', but if COMMENTS_ID_OVERRIDES is defined,
    returns the key defined by user.
    """
    COMMENTS_ID_OVERRIDES = getattr(settings, 'COMMENTS_ID_OVERRIDES', {})
    class_identifier = f"{model._meta.app_label}.{model.__name__}"
    if class_identifier in COMMENTS_ID_OVERRIDES:
        return COMMENTS_ID_OVERRIDES[class_identifier]
    else:
        return 'pk'


def get_key_value(target_object):
    """
    Get key of the model.

    By default returns 'pk', but if COMMENTS_ID_OVERRIDES is defined,
    returns the key defined by user.
    """
    key = get_key(target_object.__class__)
    if key == 'pk':
        return force_str(target_object._get_pk_val())
    else:
        return force_str(getattr(target_object, key))
