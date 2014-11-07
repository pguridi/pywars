from .models import UserProfile
from django import forms
from django_ace import AceWidget


class BotBufferForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['code']
        widgets = {
            "code": AceWidget(  mode='python',
                                theme='twilight',
                                width="850px",
                                height="500px"),
        }

    def clean_code(self):
        value = self.cleaned_data["code"]
        #if not "my_buffer" in value:
        #    raise forms.ValidationError("Must contain the string 'valid'")
        return value