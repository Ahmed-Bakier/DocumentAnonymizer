# articles/views/__init__.py

from .views_author import (
    ArticleUploadView,
    ArticleStatusQuery,
    ArticleReviseView,
)

from .views_editor import (
    ArticleListView,
    AnonymizeArticleView,
    AssignReviewerView,
    LogRecordListView,
)

from .views_reviewer import (
    ReviewerListView,
    ReviewerArticleListView,
    ArticleDetailView,
    ReviewerEvaluationView,
    ReviewerEvaluationsListView
)

from .views_common import (
    MessageCreateView,
    MessageListView,
    DownloadAnonymizedPDFView,
)