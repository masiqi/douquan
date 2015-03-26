from django import forms
from deal.models import Deal, Company, Comment, Transfer, Category, SiteJoin, ContactUs

class ApiDealForm(forms.ModelForm):
    class Meta:
        model = Deal
        exclude = ('status', 'publish_status')
        
class ApiCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        
class WriteCommentForm(forms.ModelForm):
    deal = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = Comment
        exclude = ('user')

    def clean_deal(self):
        data = self.cleaned_data['deal']
        return Deal.objects.get(pk=data)
    
class WriteTransferForm(forms.ModelForm):
    deal = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = Transfer
        exclude = ('user', 'name', 'category', 'detail', 'status', 'created_at', 'updated_at', 'tags')

    def clean_deal(self):
        data = self.cleaned_data['deal']
        return Deal.objects.get(pk=data)
    
class WriteReviewForm(forms.Form):
    act = forms.CharField(widget=forms.HiddenInput())
    deal_id = forms.IntegerField(widget=forms.HiddenInput())
    mydeal_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    tag = forms.CharField(max_length=200, required=False)
    vote = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    comment = forms.CharField(max_length=500, required=False)
    
class AdminAddCateForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)
    ids = forms.CharField(max_length=500, widget=forms.HiddenInput(), required=True)
    
class AdminAddTagForm(forms.Form):
    tag = forms.CharField(max_length=500, required=True)
    ids = forms.CharField(max_length=500, widget=forms.HiddenInput(), required=True)

class SiteJoinForm(forms.ModelForm):
    class Meta:
        model = SiteJoin
        exclude = ('created_at',) 
        
    def __init__(self, *args, **kwargs):
        super(SiteJoinForm, self).__init__(*args, **kwargs)
        self.fields['site_name'].widget.attrs['class'] = "input_01"
        self.fields['site_domain'].widget.attrs['class'] = "input_01"
        self.fields['online_date'].widget.attrs['class'] = "input_01"
        self.fields['owner'].widget.attrs['class'] = "input_01"
        self.fields['email'].widget.attrs['class'] = "input_01"
        self.fields['im'].widget.attrs['class'] = "input_01"
        self.fields['phone'].widget.attrs['class'] = "input_01"
        self.fields['address'].widget.attrs['class'] = "input_01"
        self.fields['exchange'].widget.attrs['class'] = "input_01"

class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        exclude = ('created_at',)

    def __init__(self, *args, **kwargs):
        super(ContactUsForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = "input_01"
        self.fields['content'].widget.attrs['class'] = "textarea_01"

class DealTransferAddStepOneForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class':'input_01'}))
    step = forms.IntegerField(required=True, widget=forms.HiddenInput())
    
class DealTransferAddStepTwoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(MydealAddStepTwoForm, self).__init__(*args, **kwargs)
        self['field'].attr = "foo"
    
    deal = forms.IntegerField(required=False, widget=forms.HiddenInput())
    step = forms.IntegerField(required=True, widget=forms.HiddenInput())
    city = forms.CharField(required=True, widget=forms.HiddenInput())
    status = forms.IntegerField(required=True, widget=forms.HiddenInput(), initial='1')
    
    class Meta:
        model = Transfer
        exclude = ('user', 'deal', 'city', 'created_at', 'updated_at', 'tags')
        
    def __init__(self, *args, **kwargs):
        super(DealTransferAddStepTwoForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "input_01"
        self.fields['category'].widget.attrs['class'] = "select_01"
        self.fields['detail'].widget.attrs['class'] = "textarea_01"
        self.fields['price'].widget.attrs['class'] = "input_01"
        self.fields['count'].widget.attrs['class'] = "input_01"
        self.fields['type'].widget.attrs['class'] = "select_01"
        self.fields['contact'].widget.attrs['class'] = "input_01"
