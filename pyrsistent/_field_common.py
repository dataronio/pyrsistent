from collections import Iterable
from pyrsistent import CheckedType


def _set_fields(dct, bases, name):
    dct[name] = dict(sum([list(b.__dict__.get(name, {}).items()) for b in bases], []))

    for k, v in list(dct.items()):
        if isinstance(v, _PField):
            dct[name][k] = v
            del dct[k]


def serialize(fields, format, key, value):
    serializer = fields[key].serializer
    if isinstance(value, CheckedType) and serializer is _PFIELD_NO_SERIALIZER:
        return value.serialize(format)

    return serializer(format, value)


def _check_type(destination_cls, field, name, value):
    if field.type and not any(isinstance(value, t) for t in field.type):
        actual_type = type(value)
        message = "Invalid type for field {0}.{1}, was {2}".format(destination_cls.__name__, name, actual_type.__name__)
        raise PTypeError(destination_cls, name, field.type, actual_type, message)


class _PField(object):
    __slots__ = ('type', 'invariant', 'initial', 'mandatory', 'factory', 'serializer')

    def __init__(self, type, invariant, initial, mandatory, factory, serializer):
        self.type = type
        self.invariant = invariant
        self.initial = initial
        self.mandatory = mandatory
        self.factory = factory
        self.serializer = serializer

_PFIELD_NO_TYPE = ()
_PFIELD_NO_INVARIANT = lambda _: (True, None)
_PFIELD_NO_FACTORY = lambda x: x
_PFIELD_NO_INITIAL = object()
_PFIELD_NO_SERIALIZER = lambda _, value: value


def field(type=_PFIELD_NO_TYPE, invariant=_PFIELD_NO_INVARIANT, initial=_PFIELD_NO_INITIAL,
          mandatory=False, factory=_PFIELD_NO_FACTORY, serializer=_PFIELD_NO_SERIALIZER):
    """
    Field specification factory for :py:class:`PRecord`.

    :param type: a type or iterable with types that are allowed for this field
    :param invariant: a function specifying an invariant that must hold for the field
    :param initial: value of field if not specified when instantiating the record
    :param mandatorty: boolean specifying if the field is mandatory or not
    :param factory: function called when field is set.
    :param serializer: function that returns a serialized version of the field
    """

    types = set(type) if isinstance(type, Iterable) else set([type])

    # If no factory is specified and the type is another CheckedType use the factory method of that CheckedType
    if factory is _PFIELD_NO_FACTORY and len(types) == 1 and issubclass(tuple(types)[0], CheckedType):
        # TODO: Should this option be looked up at execution time rather than at field construction time?
        #       that would allow checking against all the types specified and if none matches the
        #       first
        factory = tuple(types)[0].create

    field = _PField(type=types, invariant=invariant, initial=initial, mandatory=mandatory,
                    factory=factory, serializer=serializer)

    _check_field_parameters(field)

    return field


def _check_field_parameters(field):
    for t in field.type:
        if not isinstance(t, type):
            raise TypeError('Type paramenter expected, not {0}'.format(type(t)))

    if field.initial is not _PFIELD_NO_INITIAL and field.type and not any(isinstance(field.initial, t) for t in field.type):
        raise TypeError('Initial has invalid type {0}'.format(type(t)))

    if not callable(field.invariant):
        raise TypeError('Invariant must be callable')

    if not callable(field.factory):
        raise TypeError('Factory must be callable')

    if not callable(field.serializer):
        raise TypeError('Serializer must be callable')


class PTypeError(TypeError):
    """
    Raised when trying to assign a value with a type that doesn't match the declared type.

    Attributes:
    source_class -- The class of the record
    field -- Field name
    expected_types  -- Types allowed for the field
    actual_type -- The non matching type
    """
    def __init__(self, source_class, field, expected_types, actual_type, *args, **kwargs):
        super(PTypeError, self).__init__(*args, **kwargs)
        self.source_class = source_class
        self.field = field
        self.expected_types = expected_types
        self.actual_type = actual_type
