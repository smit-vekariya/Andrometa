
from django.urls import path, include
from .ask_me import AskMeAnything
from .rag_document import DocQuestionAnswer, RagDocuments

app_name = "ai"

urlpatterns = [
    # ask_me.py
    path('ask_me_anything/', AskMeAnything.as_view(), name='ask_me_anything'),
    # rag_document.py
    path('rag_document/', RagDocuments.as_view(), name='rag_document'),
    path('doc_question_answer/', DocQuestionAnswer.as_view(), name='doc_question_answer')
]