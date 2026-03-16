from pypdf import PdfReader
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from chromadb import Documents, EmbeddingFunction, Embeddings
import chromadb.utils.embedding_functions as embedding_functions
from typing import List
from django.http import HttpResponse
from manager.manager import create_from_exception
import chromadb, re, logging, os, json
import google.generativeai as genai


class RagDocuments(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        try:
            chunk_file_text = self.load_file(os.getcwd() + r'/ai/files/Vishal resume.pdf')
            db, name = self.get_or_create_chroma_db(documents=chunk_file_text, path=os.getcwd() + r"/ai", name="rag_experiment")
            return HttpResponse(json.dumps({"status": 1, "message": "Document upload done."}))
        except Exception as e:
            logging.exception("Something went wrong.")
            create_from_exception(e)
            return HttpResponse(json.dumps({"status": 0, "message": str(e)}))

    def get_or_create_chroma_db(self, documents:List, path:str, name:str):

        embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=settings.GEMINI_API_KEY)
        # embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=settings.OPENAI_API_KEY, model_name="text-embedding-3-small")

        chroma_client = chromadb.PersistentClient(path=path)
        db = chroma_client.get_or_create_collection(name=name, embedding_function=embedding_function)

        for index, data in enumerate(documents):
            db.add(documents=data, ids=str(index))

        return db, name

    def load_file(self, file_path):
        reader = PdfReader(file_path)
        file_text = ""
        for page in reader.pages:
            file_text += page.extract_text()

        split_text = re.split('\n \n', file_text)
        chunk_file_text = [text for text in split_text if text != ""]

        return chunk_file_text
      

class DocQuestionAnswer(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        try:
            query = self.request.query_params.get("query")

            embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=settings.GEMINI_API_KEY)
            # embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=settings.OPENAI_API_KEY, model_name="text-embedding-3-small")

            chroma_client = chromadb.PersistentClient(path=os.getcwd() + r"/ai")
            collection = chroma_client.get_collection(name="rag_experiment", embedding_function=embedding_function)

            passage = collection.query(query_texts=[query], n_results=5)
            response = self.get_gemini_response(query, passage["documents"][0])
            return HttpResponse(json.dumps({"data":[{"message":response}], "status": 1, "message": "Generation Done."}))
        except Exception as e:
            logging.exception("Something went wrong.")
            create_from_exception(e)
            return HttpResponse(json.dumps({"status": 0, "message": str(e)}))

    def get_gemini_response(self, query, passage):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(self.build_prompt(query, passage))
        return response.text

    def build_prompt(self, query, passage):
        passage = " ".join(passage)
        escaped = passage.replace("'", "").replace('"', "").replace("\n", " ")
        prompt = f"""
            You're a helpful assistant who explains things clearly and simply, like you're talking to someone without a technical background.
            Use any useful information available to give a clear, friendly, and complete answer to the question.
            Focus on being informative without sounding overly technical or formal.
            Do not mention or refer to where the information came from—just answer naturally as if you're explaining it based on what you know.
            Only use information in the PASSAGE to answer the QUESTION. Don't assume anything outside of it.
            Respond in a friendly, non-technical tone.
            If something isn’t directly relevant, feel free to leave it out.

            QUESTION: {query}
            PASSAGE: {escaped}

            Your response:
        """
        return prompt