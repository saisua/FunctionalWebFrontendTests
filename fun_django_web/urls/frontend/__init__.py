from .index import urlpatterns as index_urlpatterns
from .tests import urlpatterns as test_urlpatterns

urlpatterns = [
    *index_urlpatterns,
    *test_urlpatterns,
]
