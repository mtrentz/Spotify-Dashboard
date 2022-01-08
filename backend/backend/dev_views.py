from rest_framework.views import APIView
from rest_framework.response import Response

# Dev only
import requests


# This is used to simulate a frontend. Where user will be redirected, and then I'll be able to get the auth CODE
# the auth code then has to be sent to the backend again to get access/refresh tokens
class HomeView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        # Send code to a backend view
        requests.post("http://localhost:8000/api/spotify/token/", {"code": code})
        # view(request, code=code)
        return Response({"Code": code})
