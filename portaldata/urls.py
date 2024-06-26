from django.urls import path

from portaldata.views.profile_views import view_profile
from .views.home_views import documentation, index, send_message_by_admins, send_message_by_ms
from .views.admin_views import (
    GeneralIndicatorCreateView,
    GeneralIndicatorListView,
    GeneralIndicatorUpdateView,
    IndicatorCreateView,
    IndicatorListtableView,
    IndicatorUpdateView,
    FocusAreaListView,
    FocusAreaCreateView,
    FocusAreaUpdateView,
    ReportingPeriodCreateView,
    ReportingPeriodListView,
    ReportingPeriodUpdateView,
    indicator_list_view,
    manage_indicatorassignment,
    publish_data,
)

from .views.indicator_data_views import (
    ViewIndicatorDatatableView,
    data_entry_progress_by_ms,
    manage_general_indicatordata,
    manage_indicatordata,
    manage_indicatordata_organisation,
    show_indicator_definition,
    submit_indicator_data_by_ms,
    data_entry_progress_by_org,
    submit_indicator_data_by_org,
    view_indicatordata,
)

from .views.exchangerate_data_views import exchange_rate_data

from .views.indicator_data_validation import (
    IndicatorDatatableView,
    indicatordata_list_view,
    validate_data,
    send_back_for_revision,
)


app_name = "portaldata"

urlpatterns = [
    path("", index, name="index"),
    path("create-indicator/", IndicatorCreateView.as_view(), name="createindicator"),
    #'''Page to show the list of indicators to be validated'''
    path("manage-indicators/", indicator_list_view, name="manageindicators"),
    #''' Ajax page to feed data to the page described above'''
    path(
        "manage-indicator-ajax/",
        IndicatorListtableView.as_view(),
        name="manage-indicator-ajax",
    ),
    path(
        "update-indicator/<int:pk>/",
        IndicatorUpdateView.as_view(),
        name="updateindicator",
    ),
    path("manage-focus-area/", FocusAreaListView.as_view(), name="managefocusarea"),
    path("create-focus-area/", FocusAreaCreateView.as_view(), name="createfocusarea"),
    path(
        "update-focus-area/<int:pk>/",
        FocusAreaUpdateView.as_view(),
        name="updatefocusarea",
    ),
    path(
        "manage-reporting-period/",
        ReportingPeriodListView.as_view(),
        name="managereportingperiod",
    ),
    path(
        "create-reporting-period/",
        ReportingPeriodCreateView.as_view(),
        name="createreportingperiod",
    ),
    path(
        "update-reporting-period/<int:pk>/",
        ReportingPeriodUpdateView.as_view(),
        name="updatereportingperiod",
    ),
    path(
        "indicator-assignment/", manage_indicatorassignment, name="indicator-assignment"
    ),
    path(
        "manage-general-indicator/",
        GeneralIndicatorListView.as_view(),
        name="managegeneralindicators",
    ),
    path(
        "create-general-indicator/",
        GeneralIndicatorCreateView.as_view(),
        name="creategeneralindicator",
    ),
    path(
        "update-general-indicator/<int:pk>/",
        GeneralIndicatorUpdateView.as_view(),
        name="updategeneralindicator",
    ),
    # '''Data Entry Progress Page URL for Member States'''
    path("data-entry-by-ms/", data_entry_progress_by_ms, name="dataentrybyms"),
    # '''Data Entry Progress for Organisations'''
    path("data-entry-by-org/", data_entry_progress_by_org, name="dataentrybyorg"),
    # Data Entry Page for SADC - For General Indicators
    path(
        "manage-general-indicator-data/",
        manage_general_indicatordata,
        name="dataentrybysadc",
    ),
    # '''Data Entry Page for Member States - For a selected Focus Area'''
    path(
        "manage-indicator-data/<int:id>/",
        manage_indicatordata,
        name="manage_indicatordata",
    ),
    # '''Data Entry Page for Organizations - for a selected indicator'''
    path(
        "manage-indicator-data-org/<int:id>/",
        manage_indicatordata_organisation,
        name="manage_indicatordata_organisation",
    ),
    # '''Page to show the list of indicators data completed by Member States'''
    path(
        "view-indicator-data/",
        view_indicatordata,
        name="view-indicator-data",
    ),
    # '''Ajax page to feed data to the page described above'''
    path(
        "view-indicator-data-ajax/",
        ViewIndicatorDatatableView.as_view(),
        name="view-indicator-data-ajax",
    ),
    # '''Exchange data entry page for Member States'''
    path("dataentrybyms/exchange-rate", exchange_rate_data, name="exchange-rate"),
    path("show-definition/<int:id>/",
         show_indicator_definition, name="showdefinition"),
    # '''Indicator Submit Page (for Submit button) for Member States'''
    path("submit-indicator-data/", submit_indicator_data_by_ms,
         name="submitIndicatorData"),
    # '''Indicator Submit Page for Organizations'''
    path(
        "submit-indicator-data-by-org/",
        submit_indicator_data_by_org,
        name="submitIndicatorDatabyOrg",
    ),
    # '''Start indicator Validation'''
    # '''Page to show the list of indicators to be validated'''
    path(
        "validate-indicator-data/",
        indicatordata_list_view,
        name="validate-indicator-data",
    ),
    # '''Ajax page to feed data to the page described above'''
    path(
        "manage-indicator-data-ajax/",
        IndicatorDatatableView.as_view(),
        name="manage-indicator-data-ajax",
    ),
    # '''Validate data button'''
    path("validate-data/", validate_data, name="validate-data"),
    # '''Send back to revision button'''
    path("sendback/<int:id>/", send_back_for_revision, name="sendback"),
    # '''End indicator validation'''
    # '''Profile'''
    path("manage-profile/", view_profile, name="profile"),
    # '''Documentation'''
    path("documentation/", documentation, name="documentation"),
    # '''Send Message for Admins'''
    path("send-message-admin/", send_message_by_admins, name="send-message-admin"),
    # '''Send Message for Member States'''
    path("send-message-ms/", send_message_by_ms, name="send-message-ms"),
    # '''Publish'''
    path("publish-data/", publish_data, name="publish-data"),
]
