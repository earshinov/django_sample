from django.contrib import admin
from django.urls import path, include

from queryset_annotate_with_lookup.urls import urlpatterns as queryset_annotate_with_lookup_urls
from ordering_by_expression.urls import urlpatterns as ordering_by_expression_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('queryset_annotate_with_lookup/', include(queryset_annotate_with_lookup_urls)),
    path('ordering_by_expression/', include(ordering_by_expression_urls)),
]
