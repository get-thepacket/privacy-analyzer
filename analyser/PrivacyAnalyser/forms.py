from django import forms


class policy(forms.Form):
    policy_text = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'id':'exampleFormControlTextarea1'}), label='')

