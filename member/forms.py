from django import forms
from django.utils.translation import ugettext_lazy as _
from member.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput())
    goto = forms.CharField(max_length=200, widget=forms.HiddenInput())
    
    class Meta:
        model = User
        exclude = ('status')
        
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=20, widget=forms.PasswordInput())
    remember = forms.BooleanField(required=False)
    goto = forms.CharField(max_length=200, widget=forms.HiddenInput(), required=False)
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.cache_user = None
        super(LoginForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        try:
            user = User.objects.get(email=self.cleaned_data.get('email'))
            if user.password == self.cleaned_data.get('password'):
                self.cache_user = user
            else:
                raise forms.ValidationError(_("wrong password"))
        except User.DoesNotExist:
            raise forms.ValidationError(_("user not exist"))
        return self.cleaned_data
        
    def get_user(self):
        return self.cache_user

class ProfileForm(forms.ModelForm):
    name = forms.CharField(max_length=16, widget=forms.TextInput(attrs={'class':'input_01'}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={'class':'input_01'}))
    goto = forms.CharField(max_length=200, widget=forms.HiddenInput())
    
    class Meta:
        model = User
        exclude = ('email','status')
        
    def get_user(self):
        return self.cache_user        
        
