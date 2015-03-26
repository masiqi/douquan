from django import forms
from django.utils.translation import ugettext_lazy as _
from i.models import Mydeal

class MydealAddStepOneForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class':'input_01'}))
    url = forms.URLField(max_length=255, widget=forms.TextInput(attrs={'class':'input_01'}))
    step = forms.IntegerField(required=True, widget=forms.HiddenInput())
    
class MydealAddStepTwoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(MydealAddStepTwoForm, self).__init__(*args, **kwargs)
        self['field'].attr = "foo"
    
    deal = forms.IntegerField(required=False, widget=forms.HiddenInput())
    step = forms.IntegerField(required=True, widget=forms.HiddenInput())
    
    class Meta:
        model = Mydeal
        exclude = ('user', 'deal', 'created_at', 'updated_at', 'tags')
        
    def __init__(self, *args, **kwargs):
        super(MydealAddStepTwoForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "input_01"
        self.fields['url'].widget.attrs['class'] = "input_01"
        self.fields['site'].widget.attrs['class'] = "input_01"
        self.fields['price'].widget.attrs['class'] = "input_01"
        self.fields['account'].widget.attrs['class'] = "input_01"
        self.fields['type'].widget.attrs['class'] = "select_01"
        self.fields['status'].widget.attrs['class'] = "select_01"
        self.fields['used_at'].widget.attrs['class'] = "input_01"
        self.fields['limit'].widget.attrs['class'] = "select_01"
        self.fields['deadline'].widget.attrs['class'] = "input_01"
        self.fields['reserve'].widget.attrs['class'] = "input_01"
 