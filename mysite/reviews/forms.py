from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content', 'photo']
        widgets = {
            'rating': forms.Select(
                choices=[(5, '5/5'), (4, '4/5'), (3, '3/5'), (2, '2/5'), (1, '1/5')],
                attrs={'class': 'form-select'},
            ),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'rating': _('Įvertinimas'),
            'content': _('Atsiliepimo tekstas'),
            'photo': _('Nuotrauka'),
        }

    def clean_content(self):
        value = (self.cleaned_data.get('content') or '').strip()
        if not value:
            raise forms.ValidationError(_('Atsiliepimo tekstas yra privalomas.'))
        return value

