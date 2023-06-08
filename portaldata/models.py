from django.template.defaultfilters import linebreaksbr
from django.contrib import admin
from django.core.cache import cache
from django.db.models.constraints import UniqueConstraint
from django.core.exceptions import NON_FIELD_ERRORS
from django.db.models.signals import post_save
from email.policy import default
import imp
from operator import truediv
from random import choices
from tabnanny import verbose
from django.utils.html import html_safe, format_html

# from unittest.util import _MAX_LENGTH
from django.db import models
from django.db.models import Count, Q
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import datetime
from collections import namedtuple
from django.dispatch import receiver
from django.utils.text import slugify
import random
import string
from django.utils.safestring import SafeText, mark_safe
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.translation import gettext_lazy as _

from core.views import Get_Reporting_Year


DATA_TYPE = namedtuple(
    "DATA_TYPE",
    "currency number decimal percentage text select text_area url email date",
)._make(range(10))

IND_ASSIGNED_TO = namedtuple(
    "IND_ASSIGNED_TO", "MEMBER_STATES ORGANIZATIONS SADC"
)._make(["M", "O", "S"])


INDICATORDATA_STATUS = namedtuple("STATUS", "draft ready returned validated")._make(
    range(1, 5)
)

CHART_TYPE = namedtuple(
    "CHART_TYPE", "column line stacked stacked100pct spiderweb sunburst"
)._make(range(6))


# def generate_unique_slug(klass, field, id, identifier='slug'):
#     """
#     generate unique slug.
#     """

#     origin_slug = slugify(field)
#     unique_slug = origin_slug
#     numb = 1
#     mapping = {
#         identifier: unique_slug,
#     }
#     obj = klass.objects.filter(**mapping).first()
#     while obj:
#         if obj.id == id:
#             break
#         rnd_string = random.choices(
#             string.ascii_lowercase, k=(len(unique_slug)))
#         unique_slug = '%s-%s-%d' % (origin_slug,
#                                     ''.join(rnd_string[:10]), numb)
#         mapping[identifier] = SafeText(unique_slug)
#         numb += 1
#         obj = klass.objects.filter(**mapping).first()
#     return unique_slug


class FocusArea(models.Model):

    """Focus Area Model"""

    FOCUSAREA_STATUS_CHOICES = [(True, "Active"), (False, "Inactive")]

    sn = models.IntegerField(verbose_name="S/N", unique=True, blank=True)
    title = models.CharField(verbose_name="Focus Area", max_length=255)
    abbreviation = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    focusarea_status = models.BooleanField(
        choices=FOCUSAREA_STATUS_CHOICES,
        default=True,
    )
    created_date = models.DateTimeField(
        auto_now_add=True)  # only during the creation

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="Focus_Area_Created_By",
        on_delete=models.DO_NOTHING,
    )
    last_update = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="Focus_Area_Updated_By",
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return self.title

    def count_core_indicators(self):
        ind_count = (
            Indicator.objects.filter(focus_area=self)
            .filter(indicator_type="Core")
            .count()
        )
        return ind_count

    def count_extended_indicators(self):
        ind_count = (
            Indicator.objects.filter(focus_area=self)
            .filter(indicator_type="Extended")
            .count()
        )
        return ind_count

    def count_active_indicators(self):
        ind_count = (
            Indicator.objects.filter(focus_area=self).filter(
                status="Active").count()
        )
        return ind_count

    def count_archived_indicators(self):
        ind_count = (
            Indicator.objects.filter(focus_area=self).filter(
                status="Archived").count()
        )
        return ind_count

    def count_required_indicators(self):
        ind_count = (
            Indicator.objects.filter(focus_area=self).filter(
                required=True).count()
        )
        return ind_count

    def count_active_required_indicators(self):
        ind_count = (
            Indicator.objects.filter(focus_area=self, required=True)
            .filter(status="Active")
            .count()
        )
        return ind_count

    def count_optional_indicators(self):
        ind_count = (
            Indicator.objects.filter(focus_area=self).filter(
                required=False).count()
        )
        return ind_count

    def count_active_required_indicators_by_assignment(self, assignedto):
        ind_count = (
            Indicator.objects.filter(
                focus_area__focusarea_status=True,
                focus_area=self,
                required=True,
                indicator_assigned_to=assignedto,
            )
            .filter(status="Active")
            .count()
        )
        return ind_count

    def count_completed_indicators_by_assignment(
        self, assignedto, memberstate, reporting_year
    ):
        ind_count = (
            IndicatorData.objects.filter(
                indicator__focus_area=self,
                indicator__focus_area__focusarea_status=True,
                indicator__indicator_assigned_to=assignedto,
                member_state=memberstate,
                reporting_year=reporting_year,
            )
            .exclude(value_NA=False, ind_value__exact="")
            .exclude(value_NA=False, ind_value__isnull=True)
            .exclude(indicator__required=False)
            .count()
        )
        return ind_count

    def check_submitted(self, assignedto, memberstate, reporting_year):
        ind_count = IndicatorData.objects.filter(
            indicator__focus_area=self,
            indicator__indicator_assigned_to=assignedto,
            reporting_year=reporting_year,
            member_state=memberstate,
            submitted=False,
        ).count()

        return ind_count

    def get_revision_request(self, assignedto, memberstate, reporting_year):
        ind_count = IndicatorData.objects.filter(
            indicator__focus_area=self,
            indicator__indicator_assigned_to=assignedto,
            reporting_year=reporting_year,
            member_state=memberstate,
            submitted=False,
            validation_status=INDICATORDATA_STATUS.returned,
        ).count()

        return ind_count

    def count_indicators(self):
        ind_count = (
            Indicator.objects.filter(focus_area=self)
            .exclude(indicator_assigned_to=IND_ASSIGNED_TO.ORGANIZATIONS)
            .exclude(indicator_assigned_to=IND_ASSIGNED_TO.SADC)
            .count()
        )
        return ind_count

    def next_sn(self):
        """Return Serial Number for a new indicator (count + 1)"""
        next_sn = FocusArea.objects.count() + 1
        return next_sn

    class Meta:
        ordering = ["sn"]
        verbose_name_plural = "Focus Areas"

        verbose_name = "Focus Area"


class MemberState(models.Model):

    """Model for Member States"""

    MEMBERSTATE_STATUS_CHOICES = [(True, "Active"), (False, "Inactive")]

    member_state = models.CharField(
        max_length=255, unique=True, verbose_name="Memeber State"
    )
    member_state_short_name = models.CharField(
        max_length=30, blank=True, verbose_name="Short Name"
    )

    member_state_iso3_code = models.CharField(
        max_length=3, verbose_name="ISO 3 Code", blank=True
    )

    memberstate_status = models.BooleanField(
        choices=MEMBERSTATE_STATUS_CHOICES, default=True, verbose_name="Status"
    )

    @property
    def ms_shortname(self):
        if self.member_state_short_name != None or self.member_state_short_name != '':
            return self.member_state_short_name
        else:
            return self.member_state

    def count_active(self):
        active_member_states = MemberState.objects.filter(
            memberstate_status=True
        ).count()
        return active_member_states

    def __str__(self):
        return self.member_state

    class Meta:
        ordering = ["member_state"]
        verbose_name_plural = "Member States"


class Indicator(models.Model):

    """Model for Indicators"""

    DATA_TYPE = [
        (DATA_TYPE.currency, "Currency"),
        (DATA_TYPE.number, "Whole Number"),
        (DATA_TYPE.decimal, "Decimal"),
        (DATA_TYPE.percentage, "Percentage"),
        (DATA_TYPE.text, "Text"),
        (DATA_TYPE.select, "Select (Yes/No)"),
        (DATA_TYPE.text_area, "Text Area"),
        (DATA_TYPE.url, "URL"),
        (DATA_TYPE.email, "Email"),
        (DATA_TYPE.date, "Date"),
    ]

    INDICATOR_TYPE_CHOICES = [
        ("Core", "Core"),
        ("Extended", "Extended"),
    ]

    INDICATOR_STATUS_CHOICES = [("Active", "Active"), ("Archived", "Archived")]

    CURRENCY_TYPE_CHOICES = [("usd", "USD"), ("local", "Local Currency")]

    INDICATOR_ASSIGNED_TO_GROUPS = [
        (IND_ASSIGNED_TO.MEMBER_STATES, "Member States"),
        (IND_ASSIGNED_TO.ORGANIZATIONS, "Organisations"),
        (IND_ASSIGNED_TO.SADC, "SADC"),
    ]

    YESNO_CHOICES = [(True, "Yes"), (False, "No")]

    focus_area = models.ForeignKey(
        FocusArea, on_delete=models.PROTECT, verbose_name="Focus Area"
    )

    indicator_number = models.CharField(
        max_length=50, unique=True, verbose_name="Indicator Number"
    )

    label = models.CharField(
        "Indicator", max_length=255, help_text="Enter the indicator here"
    )

    data_type = models.PositiveSmallIntegerField(
        choices=DATA_TYPE, verbose_name="Data Type"
    )

    choices = models.TextField(
        blank=True,
        help_text="if Data Type is Select, fill in the option separated by commas. ex: Yes, No or Male, Female",
    )

    type_of_currency = models.CharField(
        max_length=20, choices=CURRENCY_TYPE_CHOICES, blank=True, null=True
    )

    definition = models.TextField()

    source = models.CharField(max_length=50, blank=True)

    indicator_type = models.CharField(
        max_length=8,
        choices=INDICATOR_TYPE_CHOICES,
        default="Core",
        verbose_name="Indicator Type",
    )

    status = models.CharField(
        max_length=10,
        choices=INDICATOR_STATUS_CHOICES,
        default="Active",
        verbose_name="Status",
    )

    required = models.BooleanField(
        verbose_name="Is required ? ",
        choices=YESNO_CHOICES,
        default=True,
    )

    attachment = models.BooleanField(
        verbose_name="Has attachment ? ",
        choices=YESNO_CHOICES,
        default=False,
    )

    indicator_assigned_to = models.CharField(
        max_length=1, choices=INDICATOR_ASSIGNED_TO_GROUPS
    )

    created_date = models.DateTimeField(
        auto_now_add=True)  # only during the creation

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="Indicator_Created_By",
        on_delete=models.DO_NOTHING,
    )

    last_update = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="Indicator_Updated_By",
        on_delete=models.DO_NOTHING,
    )

    def datatype(self):
        key_list = DATA_TYPE._fields[self.data_type].capitalize()

        return key_list

    def count_completed_required_indicators(self):
        ind_count = (
            IndicatorData.objects.filter(
                indicator=self,
                indicator__focus_area__focusarea_status=True,
                member_state__memberstate_status=True,
                reporting_year=Get_Reporting_Year(),
            )
            .exclude(value_NA=False, ind_value__exact="")
            .exclude(value_NA=False, ind_value__isnull=True)
            .exclude(indicator__required=False)
            .count()
        )

        return ind_count

    def active_member_states(self):
        ms = MemberState()
        return ms.count_active()

    def calculate_progress(self):
        ms = MemberState()

        if ms.count_active() == 0:
            return 0
        else:
            ind_progress = round(
                self.count_completed_required_indicators() / ms.count_active() * 100
            )
            return ind_progress

    def check_submitted(self):
        ind_count = IndicatorData.objects.filter(
            reporting_year=Get_Reporting_Year(),
            indicator__focus_area__focusarea_status=True,
            indicator__focus_area=self,
            submitted=False,
        ).count()

        return ind_count

    def get_revision_request(self, org, reporting_year):
        ind_count = IndicatorData.objects.filter(
            reporting_year=reporting_year,
            indicator__focus_area__focusarea_status=True,
            indicator=self,
            submitted=False,
            indicator__assignedindicator__assigned_to_organisation=org,
            validation_status=INDICATORDATA_STATUS.returned,
        ).count()

        return ind_count

    def __str__(self):
        return self.label

    class Meta:
        ordering = ["pk"]


class Currency(models.Model):

    """Model for Currencies to be managed by Admin"""

    member_state = models.OneToOneField(MemberState, on_delete=models.PROTECT)
    currency_label = models.CharField(max_length=25)
    currency_short_name = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.currency_label

    class Meta:
        ordering = ["member_state"]
        verbose_name_plural = "Currencies"


class Organisation(models.Model):

    """Model for Organisations"""

    ORGANISATION_STATUS_CHOICES = [(True, "Active"), (False, "Inactive")]

    organisation_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    organisation_status = models.BooleanField(
        choices=ORGANISATION_STATUS_CHOICES,
        default=True,
    )

    def __str__(self):
        return self.organisation_name


class AssignedIndicator(models.Model):
    """
    Model for Assigning Indicators
    Indicators are assigned to user types (Member States or Organisations)
    """

    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)

    assigned_to_organisation = models.ForeignKey(
        Organisation,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Assigned to",
    )

    created_date = models.DateTimeField(
        auto_now_add=True)  # only during creation

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="IndicatorAssignment_Created_By",
        on_delete=models.DO_NOTHING,
    )

    last_update = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="IndicatorAssignment_Updated_By",
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return self.indicator.label

    class Meta:
        unique_together = ("indicator", "assigned_to_organisation")
        verbose_name_plural = "Assigned Indicators"


class ReportingPeriod(models.Model):

    """Model for Reporting Periods"""

    reporting_start_date = models.DateField(
        verbose_name="Reporting Start Date")
    reporting_end_date = models.DateField(verbose_name="Reporting End Date")
    current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.current:
            print(self.current)
            ReportingPeriod.objects.update(current=Q(pk=self.pk))

        super(ReportingPeriod, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-reporting_end_date"]
        verbose_name_plural = "Reporting Periods"


class IndicatorData(models.Model):

    """Table / Model that holds all indicator data entered into the system"""

    YESNO_CHOICES = [(True, "Yes"), (False, "No")]

    INDICATORDATA_STATUS_CHOICES = [
        (INDICATORDATA_STATUS.draft, "Draft"),
        (INDICATORDATA_STATUS.ready, "Ready for validation"),
        (INDICATORDATA_STATUS.returned, "Returned for revision"),
        (INDICATORDATA_STATUS.validated, "Validated"),
    ]

    reporting_year = models.CharField(
        _("Reporting Year"), max_length=6, blank=False)

    indicator = models.ForeignKey(
        Indicator, on_delete=models.PROTECT, verbose_name="Indicator"
    )

    member_state = models.ForeignKey(
        MemberState, on_delete=models.DO_NOTHING, verbose_name="Member State"
    )

    ind_value = models.TextField(verbose_name="Data", blank=True, null=True)

    ind_value_adjusted = models.TextField(
        verbose_name="Data Converted (local currency data converted to USD)",
        max_length=200,
        blank=True,
        null=True,
    )

    value_NA = models.BooleanField(
        verbose_name="Data N/A", default=False, null=True, blank=True
    )

    comments = models.TextField(blank=True)

    attachment = models.FileField(null=True, blank=True)

    submitted = models.BooleanField(
        verbose_name="Is Submitted ? ",
        choices=YESNO_CHOICES,
        default=False,
    )

    validation_status = models.IntegerField(
        choices=INDICATORDATA_STATUS_CHOICES, default=INDICATORDATA_STATUS.draft
    )

    created_date = models.DateTimeField(
        auto_now_add=True)  # only during the creation

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="Data_Created_By",
        on_delete=models.DO_NOTHING,
    )

    last_update = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="Data_Last_Updated_By",
        on_delete=models.DO_NOTHING,
    )

    @property
    def thisvalue(self):
        """Returns Humanized data (e.g. 1000 -> 1,000)"""
        if self.ind_value_adjusted:
            if (
                self.indicator.data_type == DATA_TYPE.number
                or self.indicator.data_type == DATA_TYPE.currency
                or self.indicator.data_type == DATA_TYPE.decimal
            ):
                return intcomma(self.ind_value_adjusted)
            elif self.indicator.data_type == DATA_TYPE.percentage:
                return self.ind_value_adjusted + "%"

            else:
                return self.ind_value
        else:
            return "N/A"

    @property
    def format_value(self):

        if self.value_NA == True:

            return "N/A"
        else:

            if self.ind_value:

                if (
                    self.indicator.data_type == DATA_TYPE.number
                    or self.indicator.data_type == DATA_TYPE.currency
                    or self.indicator.data_type == DATA_TYPE.decimal
                ):
                    return intcomma(self.ind_value)
                elif self.indicator.data_type == DATA_TYPE.percentage:
                    return self.ind_value + "%"

                else:
                    return self.ind_value
            else:

                return ""

    @property
    def format_submitted_status(self):
        if self.submitted:
            return "Submitted"

        else:
            return "Draft"

    # @property
    # def format_comments(self):
    #     str = linebreaksbr(self.comments)
    #     print(mark_safe(str))
    #     return mark_safe(self.comments)

    @property
    def get_validation_status(self):

        choices_dict = dict(self.INDICATORDATA_STATUS_CHOICES)

        return (choices_dict[self.validation_status])

    def focus_area(self):
        return self.indicator.focus_area

    def is_returned_for_revision(self):
        if self.validation_status == INDICATORDATA_STATUS.returned:
            return True
        else:
            return False

    def __str__(self):
        return self.indicator.label

    class Meta:
        unique_together = ("reporting_year", "indicator", "member_state")

        verbose_name_plural = "Indicator Data"

        ordering = ["-reporting_year", "member_state", "indicator"]


@ receiver(post_save, sender=IndicatorData, dispatch_uid="update_currency_usd")
def update_usd(sender, instance, **kwargs):
    """method for updating currency values to USD"""
    if instance.ind_value:
        if (
            instance.indicator.data_type == DATA_TYPE.currency
            and instance.indicator.type_of_currency != "usd"
        ):
            print(get_exchange_rate(instance.member_state, Get_Reporting_Year()))
            if get_exchange_rate(instance.member_state, Get_Reporting_Year()) != 0:
                instance.ind_value_adjusted = round(
                    float(instance.ind_value)
                    / float(
                        get_exchange_rate(
                            instance.member_state, Get_Reporting_Year())
                    ),
                    4,
                )
                print(instance.ind_value_adjusted)

        else:
            instance.ind_value_adjusted = instance.ind_value

    post_save.disconnect(
        update_usd, sender=IndicatorData, dispatch_uid="update_currency_usd"
    )
    instance.save()
    post_save.connect(
        update_usd, sender=IndicatorData, dispatch_uid="update_currency_usd"
    )


class IndicatorDataValidationHistory(models.Model):
    indicator_data = models.ForeignKey(IndicatorData, on_delete=models.CASCADE)
    previous_data = models.CharField(max_length=200)
    current = models.BooleanField(default=False)
    comments = models.TextField(blank=True)

    last_update = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="revision_last_updated_by",
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        ordering = ["-last_update"]

        verbose_name_plural = "Indicator Data Validation History"


class ExchangeRateData(models.Model):

    """Model for Exchange Rate Data"""

    YESNO_CHOICES = [(True, "Yes"), (False, "No")]

    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate_date = models.DateField(
        blank=True,
        null=True,
    )
    exchange_rate = models.FloatField(
        help_text="Exchange rate of 1 USD to local currency"
    )

    reporting_year = models.CharField(max_length=6)

    submitted = models.BooleanField(
        verbose_name="Is Submitted ? ",
        choices=YESNO_CHOICES,
        default=False,
    )

    validated = models.BooleanField(
        verbose_name="Is validated ? ",
        choices=YESNO_CHOICES,
        default=False,
    )

    last_update = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="ExchangeRate_Last_Updated_By",
        on_delete=models.DO_NOTHING,
    )

    def is_submitted(self):
        return self.submitted

    def currency_label(self):
        return self.currency.currency_label

    def member_state(self):
        return self.currency.member_state.member_state

    def __str__(self):
        return self.currency.currency_label

    class Meta:
        unique_together = ("reporting_year", "currency")
        verbose_name_plural = "Exchange Rate Data"
        ordering = ["-reporting_year", "currency__member_state"]


def get_exchange_rate(member_state, reporting_year):
    """Given Member State and Reporting year, method will return exchange rate value"""

    try:
        exchange_rate = ExchangeRateData.objects.get(
            currency__member_state=member_state, reporting_year=reporting_year
        ).exchange_rate
    except:
        exchange_rate = None
    if exchange_rate:
        return exchange_rate

    else:
        return 0


class GeneralIndicator(models.Model):

    """Model for General Indicator"""

    indicator_label = models.CharField(
        verbose_name="Indicator", max_length=200)
    definition = models.TextField(blank=True)

    include_in_chart = models.ForeignKey(
        "Chart", on_delete=models.DO_NOTHING, blank=True, null=True
    )

    series_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="If part of a chart, enter the series name. Otherwise the full Indicator Name will be used.",
    )

    last_update = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="GeneralIndicator_Last_Updated_By",
        on_delete=models.DO_NOTHING,
    )

    def __str__(self):
        return self.indicator_label

    class Meta:
        verbose_name = "General Indicator"


class GeneralIndicatorData(models.Model):

    """Model for General Indicators Data"""

    general_indicator = models.ForeignKey(
        GeneralIndicator, on_delete=models.PROTECT, verbose_name="Indicator"
    )
    indicator_value = models.CharField(verbose_name="Data", max_length=200)
    reporting_year = models.CharField(max_length=6)

    last_update = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="GeneralIndicatorData_Last_Updated_By",
        on_delete=models.DO_NOTHING,
    )

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(GeneralIndicatorData, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "General Indicator Data"

        UniqueConstraint(
            fields=["general_indicator", "reporting_year"], name="double_entry"
        )

        unique_together = ("general_indicator", "reporting_year")


class Published(models.Model):

    """Model to hold Published years data"""

    YESNO_CHOICES = [(True, "Yes"), (False, "No")]

    reporting_year = models.CharField(
        unique=True, max_length=6
    )  # , default=str(Get_Current_Year) check

    published_status = models.BooleanField(
        verbose_name="Is Published ? ",
        choices=YESNO_CHOICES,
        default=False,
    )

    last_update = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="PublishedYear_Last_Updated_By",
        on_delete=models.DO_NOTHING,
    )

    @receiver(post_save)
    def clear_the_cache(**kwargs):
        cache.clear()

    def __str__(self):
        return self.reporting_year

    class Meta:
        verbose_name_plural = "Published"
        ordering = ["-reporting_year"]


class ScoreCard(models.Model):

    """Score cards configuration"""

    AGGREGATION_CHOICES = [
        ("avg", "Average"),
        ("sum", "Total"),
    ]
    scorecard_name = models.CharField(max_length=100)
    scorecard_title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    indicator_list = models.ManyToManyField(
        Indicator, through="ScoreCardConfig")

    aggregation = models.CharField(
        max_length=10, choices=AGGREGATION_CHOICES, blank=True
    )

    def __str__(self):
        return self.scorecard_title

    class Meta:
        verbose_name_plural = "Scorecards"
        ordering = ["pk"]


class ScoreCardConfig(models.Model):

    """Scorecard configuration"""

    AGGREGATION_CHOICES = [
        ("avg", "Average"),
        ("sum", "Total"),
    ]

    CALCULATION_CHOICES = [("num", "Numerator"), ("denom", "Denominator")]

    scorecard = models.ForeignKey(ScoreCard, on_delete=models.CASCADE)

    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)

    num_denom = models.CharField(
        max_length=50,
        choices=CALCULATION_CHOICES,
        blank=True,
        verbose_name="Numerator / Denominator",
    )

    aggregation = models.CharField(
        max_length=50, choices=AGGREGATION_CHOICES, blank=True
    )

    def __str__(self):
        return self.indicator.label

    class Meta:
        verbose_name_plural = "Scorecard Configuration"
        ordering = ["scorecard__pk", "pk"]


class Chart(models.Model):

    """Model for Charts"""

    AGGREGATION_CHOICES = [
        ("avg", "Average"),
        ("sum", "Total"),
        ("yesPercentage", "Percent of Yes answers"),
    ]

    CHART_TYPE = [
        (CHART_TYPE.column, "Column Chart"),
        (CHART_TYPE.line, "Line Chart"),
        (CHART_TYPE.stacked, "Stacked Column Chart"),
        (CHART_TYPE.stacked100pct, "100% Stacked Column Chart"),
        (CHART_TYPE.spiderweb, "Spiderweb Chart"),
        (CHART_TYPE.sunburst, "Sunburst Chart"),
    ]

    chart_name = models.CharField(max_length=50)

    chart_title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    chart_type = models.PositiveSmallIntegerField(choices=CHART_TYPE)

    indicators_list = models.ManyToManyField(Indicator, through="ChartConfig")

    y_axis_title = models.CharField(max_length=100, blank=True)

    aggregation = models.CharField(
        max_length=50, choices=AGGREGATION_CHOICES, blank=True
    )

    def __str__(self):
        return self.chart_title

    class Meta:
        ordering = ["pk"]


class ChartConfig(models.Model):

    """Charts configuration"""

    EXTRA_CALCULATION_CHOICES = [
        ("per100", "Calculate Per 100"),
        ("exchangerate", "Convert Currency to USD"),
        ("mainstack", "Main Group in Stacked Chart"),
        ("yesPercentage", "Calculate Yes percentage"),
        ("mtokbits", "Covert Mbits to Kbits"),
    ]

    chart = models.ForeignKey(Chart, on_delete=models.CASCADE)

    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)

    series_name = models.CharField(max_length=200, blank=True)

    extra_calculation = models.CharField(
        max_length=50, choices=EXTRA_CALCULATION_CHOICES, blank=True
    )

    def __str__(self):
        return self.indicator.label

    class Meta:
        verbose_name_plural = "Chart Configuration"
        ordering = ["chart__pk", "pk"]
