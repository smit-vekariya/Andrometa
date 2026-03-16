from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from google import genai
from django.conf import settings
from django.http import HttpResponse
from bs4 import BeautifulSoup
import json, logging
from manager.manager import create_from_exception


client = genai.Client(api_key=settings.GEMINI_API_KEY)

class AskMeAnything(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        try:
            query_params = self.request.query_params
            query = query_params.get("query")
            query_type = query_params.get("query_type")
            if query:
                query = self.prompt_filter(query, query_type)
                data = self.ask_gemini(query)
                return HttpResponse(json.dumps({"data":[data], "status": 1, "message": "Generation Done."}))
            else:
                return HttpResponse(json.dumps({"status": 0, "message": "Query not found!"}))
        except Exception as e:
            logging.exception("Something went wrong.")
            create_from_exception(e)
            return HttpResponse(json.dumps({"status": 0, "message": str(e)}))

    def prompt_filter(self, query, query_type):
        if query_type == "mail":
            query = f"""
                Generate a professional email message and subject part only not other.
                The 'message' should include proper formatting with line breaks (\\n).
                Here's the context: {query}
                Output format: {{subject:'', message:''}}
                """

        return query

    def ask_gemini(self, query):
        response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[query]
                )

        response = (response.text).replace('```json','').replace('```','')
        json_response = json.loads(response)
        return json_response



