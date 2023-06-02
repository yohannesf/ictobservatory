from django import forms

from django_select2.forms import Select2MultipleWidget


from portaldata.models import Indicator, MemberState


class SendMessage_byAdmins(forms.Form):

    memberstate_filter_field = forms.ChoiceField(
        choices=[])
    subject = forms.CharField(max_length=200, required=True)
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(SendMessage_byAdmins, self).__init__(*args, **kwargs)

        memberstates_qs = MemberState.objects.filter(
            memberstate_status=True).values().order_by('member_state')

        MEMBERSTATE_CHOICES = sorted(tuple(set(
            [(q['id'], q['member_state']) for q in memberstates_qs])))

        MEMBERSTATE_CHOICES.insert(0, ["all", "Select All"])  # type: ignore

        self.fields['memberstate_filter_field'] = forms.MultipleChoiceField(
            choices=MEMBERSTATE_CHOICES, widget=Select2MultipleWidget)
        self.fields['memberstate_filter_field'].label = "Member States"


class SendMessage_byMS(forms.Form):

    subject = forms.CharField(max_length=200, required=True)
    message = forms.CharField(widget=forms.Textarea)

    # def __init__(self, *args, **kwargs):
    #     super(SendMessage_byMS, self).__init__(*args, **kwargs)

    #     memberstates_qs = MemberState.objects.filter(
    #         memberstate_status=True).values().order_by('member_state')

    #     MEMBERSTATE_CHOICES = sorted(tuple(set(
    #         [(q['id'], q['member_state']) for q in memberstates_qs])))

    #     MEMBERSTATE_CHOICES.insert(0, ["all", "Select All"])  # type: ignore

    #     self.fields['memberstate_filter_field'] = forms.MultipleChoiceField(
    #         choices=MEMBERSTATE_CHOICES, widget=Select2MultipleWidget)
    #     self.fields['memberstate_filter_field'].label = "Member States"
