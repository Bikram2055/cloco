from django import forms
from django.contrib.auth.models import Group
from .models import User
from django.core.validators import EmailValidator


class RegisterForm(forms.ModelForm):

    email = forms.EmailField(validators=[EmailValidator()])
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "form-control", "placeholder": f"{field}"}
            )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "dob", "phone", "address", "gender", "password"]

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data["first_name"]
        last_name = cleaned_data["last_name"]
        password = cleaned_data["password"]
        if first_name == last_name:
            raise forms.ValidationError("first name and last name is same")
        if len(str(password)) < 6:
            raise forms.ValidationError("password must be minimum of 6 digit")
        return cleaned_data