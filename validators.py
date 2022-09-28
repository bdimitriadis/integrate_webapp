import phonenumbers

from wtforms import ValidationError


class PhoneValidator(object):
    """ Custom validator for phone fields
    """
    def __init__(self, message=None):
        if not message:
            message = "Invalid phone number"
        self.message = message

    def __call__(self, form, field):
        if len(field.data) > 16:
            raise ValidationError(self.message)
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError(self.message)
        except:
            # input_number = phonenumbers.parse("+1" + field.data)
            # if not (phonenumbers.is_valid_number(input_number)):
            raise ValidationError(self.message)
