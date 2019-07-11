from django import forms
from django.contrib import admin

from verif_parser.models import Company, Director


class CompanyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CompanyAdminForm, self).__init__(*args, **kwargs)
        self.fields['directors'].queryset = self.instance.directors

    class Meta:
        model = Company
        fields = '__all__'


class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm


class DirectorAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DirectorAdminForm, self).__init__(*args, **kwargs)
        self.fields['companies'].queryset = self.instance.companies

    class Meta:
        model = Director
        fields = '__all__'


class DirectorAdmin(admin.ModelAdmin):
    form = DirectorAdminForm


class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm


admin.site.register(Company, CompanyAdmin)
admin.site.register(Director, DirectorAdmin)
