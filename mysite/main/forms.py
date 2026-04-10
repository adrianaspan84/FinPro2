from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import Profile


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label=_("Pakartoti slaptažodį"))

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError(_("Slaptažodžiai nesutampa"))
        return cleaned


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'bio',
            'phone',
            'city',
            'address',
            'is_legal_entity',
            'company_name',
            'company_code',
            'company_vat_code',
            'company_address',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

        placeholders = {
            'first_name': _("Įveskite vardą"),
            'last_name': _("Įveskite pavardę"),
            'email': 'example@email.com',
            'phone': _("0XXXXXXXX"),
            'city': _("Miestas"),
            'address': _("Adresas"),
            'company_name': _("Įmonės pavadinimas"),
            'company_code': _("Įmonės kodas"),
            'company_vat_code': _("PVM kodas"),
            'company_address': _("Juridinis adresas"),
        }

        text_fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'city',
            'address',
            'company_name',
            'company_code',
            'company_vat_code',
            'company_address',
        ]

        for field_name in text_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': placeholders[field_name],
            })

        self.fields['bio'].widget.attrs.update({
            'class': 'form-control',
            'rows': 4,
            'placeholder': _("Trumpas aprašymas apie jus"),
        })

        self.fields['avatar'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*',
        })

        self.fields['is_legal_entity'].widget.attrs.update({
            'class': 'form-check-input',
        })

    def save(self, commit=True):
        profile = super().save(commit=False)

        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            if commit:
                self.user.save()

        if not profile.is_legal_entity:
            profile.company_name = ''
            profile.company_code = ''
            profile.company_vat_code = ''
            profile.company_address = ''

        if commit:
            profile.save()
        return profile
