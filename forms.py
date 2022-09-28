import wtforms
from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import RadioField
from wtforms import SelectMultipleField
from wtforms import FieldList
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.fields.html5 import TelField
from wtforms.widgets import ListWidget
from wtforms.widgets import CheckboxInput
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Regexp
from wtforms.validators import Optional

from validators import PhoneValidator



class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


def set_label_choices(field, json_obj_element):
    field.label = wtforms.Label(field.id, json_obj_element["text"])
    if field.id == "evaluations":
        options = json_obj_element["options"]
        for indx, f in enumerate(field):
            tmp_label = "<div class=\"col-4 span-left\">{}</div><div class=\"col-4 offset-4 span-right\">{}</div>".format(
                options[indx]["left_label"],
                options[indx]["right_label"])
            f.label = wtforms.Label(f.id, tmp_label)
            f.choices = [("{}".format(el), "{}".format(el)) for el in range(options[indx]["score"][0],
                                                               options[indx]["score"][1] + 1)]

    else:
        field.choices = [("{}".format(indx), el) for indx, el in enumerate(json_obj_element["options"])]


class SurveyForm(FlaskForm):
    """ Survey form, created "dynamically" from json object data passed
    by the survey view
    """

    useful = RadioField(validators=[DataRequired()])
    interesting_components = MultiCheckboxField(validators=[DataRequired()])
    take_action = RadioField(validators=[DataRequired()])
    which_action = MultiCheckboxField(validators=[DataRequired()])
    use_again = RadioField(validators=[DataRequired()])
    gender = RadioField(validators=[DataRequired()])
    age_category = RadioField(validators=[DataRequired()])
    evaluations = FieldList(RadioField(validators=[DataRequired()]), min_entries=8, max_entries=8)
    comment = TextAreaField(validators=[Optional(), Length(max=300)], render_kw={'maxlength': 300, 'size': 300})

    def __init__(self, json_obj, **kwargs):
        super().__init__(**kwargs)

        mapping = {"useful": "question_1", "interesting_components": "question_2",
                   "take_action": "question_3", "which_action": "question_4",
                   "use_again": "question_5", "gender": "question_6",
                   "age_category": "question_7", "evaluations": "question_8", "comment": "question_9"}

        # field_names = ["useful", "interesting_components", "take_action", "which_action",
        #                "use_again", "gender", "age_category", "evaluations"]


        for field_name, question in mapping.items():
        #     # if field_name != "evaluations":
            set_label_choices(self[field_name], json_obj[question])

        # for indx, field_name in enumerate(field_names):
        #     set_label_choices(self[field_name], json_obj[indx])

    def validate(self):
        if self.take_action.data == "1":
            self.which_action.validators=[Optional()]
        return super(FlaskForm, self).validate()


class PasscodeForm(FlaskForm):
    passcode_flds = FieldList(StringField(validators=[DataRequired(message="all_fields_required"),
                                                      Regexp("^[a-zA-Z0-9]+$", message="nonalphanumeric_passcode"),
                                                      Length(min=8, max=8, message="wrong_passcode_length")],
                                          render_kw={"maxlength": 8, "size": 8, "style": "text-align: center"}),
                              min_entries=4, max_entries=4
    )


class SendMsgForm(FlaskForm):
    phone_numbers = FieldList(TelField(validators=[Optional(), PhoneValidator(message="invalid_phone")]),
                              min_entries=5, max_entries=5)
    msg = TextAreaField(validators=[DataRequired(message="required"), Length(max=360)],
                        render_kw={'readonly': True, 'rows': 10, "cols": 15})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self["phone_numbers"].entries[0].validators = [DataRequired(message="required"), PhoneValidator(message="invalid_phone")]



class TestFinderForm(FlaskForm):
    country = SelectField()
    testing_hiv = BooleanField(default=False)
    testing_hepc = BooleanField(default=False)
    testing_sti = BooleanField(default=False)

    def __init__(self, country_choices, flds_label_value={}, **kwargs):
        super().__init__(**kwargs)
        for fld in flds_label_value.keys():
            lbl, val = flds_label_value[fld]
            self[fld].label = wtforms.Label(self[fld].id, lbl)
            if fld == "country":
                self[fld].choices = country_choices
            self[fld].data = val





