from kolibri.auth.constants import collection_kinds
from kolibri.auth.models import Collection, FacilityUser
from kolibri.content.models import ContentNode
from kolibri.logger.models import ContentSummaryLog
from rest_framework import pagination, permissions, viewsets

from .serializers import ContentReportSerializer, ContentSummarySerializer, UserReportSerializer
from .utils.return_users import get_members_or_user


class OptionalPageNumberPagination(pagination.PageNumberPagination):
    """
    Pagination class that allows for page number-style pagination, when requested.
    To activate, the `page_size` argument must be set. For example, to request the first 20 records:
    `?page_size=20&page=1`
    """
    page_size = None
    page_size_query_param = "page_size"


class KolibriReportPermissions(permissions.BasePermission):

    # check if requesting user has permission for collection or user
    def has_permission(self, request, view):
        collection_kind = view.kwargs.get('collection_kind', None)
        collection_id = view.kwargs.get('collection_id', None)
        user_pk = view.kwargs.get('pk', None)

        if any(collection_kind in kind for kind in collection_kinds.choices):
            perm_check_obj = Collection.objects.get(pk=collection_id)
        elif collection_id:
            perm_check_obj = FacilityUser.objects.get(pk=collection_id)
        else:  # check necessary for usersummary endpoint
            perm_check_obj = FacilityUser.objects.get(pk=user_pk)

        return request.user.can_read(perm_check_obj)


class UserReportViewSet(viewsets.ModelViewSet):

    permission_classes = (KolibriReportPermissions,)
    pagination_class = OptionalPageNumberPagination
    serializer_class = UserReportSerializer

    def get_queryset(self):
        # only a collection should be passed to this endpoint
        assert any(self.kwargs['collection_kind'] in kind for kind in collection_kinds.choices)
        return get_members_or_user(self.kwargs['collection_kind'], self.kwargs['collection_id'])


class ContentReportViewSet(viewsets.ModelViewSet):

    permission_classes = (KolibriReportPermissions,)
    pagination_class = OptionalPageNumberPagination
    serializer_class = ContentReportSerializer

    def get_queryset(self):
        content_node_id = self.kwargs['content_node_id']
        return ContentNode.objects.filter(parent=content_node_id)


class ContentSummaryViewSet(viewsets.ModelViewSet):

    permission_classes = (KolibriReportPermissions,)
    serializer_class = ContentSummarySerializer

    def get_queryset(self):
        return ContentNode.objects.all()


class UserSummaryViewSet(viewsets.ModelViewSet):

    permission_classes = (KolibriReportPermissions,)
    serializer_class = UserReportSerializer

    def get_queryset(self):
        return FacilityUser.objects.all()


class RecentReportViewSet(viewsets.ModelViewSet):

    permission_classes = (KolibriReportPermissions,)
    pagination_class = OptionalPageNumberPagination
    serializer_class = ContentReportSerializer

    def get_queryset(self):
        query_node = ContentNode.objects.get(pk=self.kwargs['content_node_id'])
        recent_content_items = ContentSummaryLog.objects.filter_by_topic(query_node).order_by('end_timestamp').values_list('content_id')
        return ContentNode.objects.filter(content_id__in=recent_content_items)
