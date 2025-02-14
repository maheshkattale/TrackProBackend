from django.shortcuts import render,HttpResponse
import json

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            return HttpResponse(json.dumps({"n" : 0,"msg" : "The source is invalid","status":404}), content_type="application/json")
        return response
