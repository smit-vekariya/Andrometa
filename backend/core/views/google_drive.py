from django.http import HttpResponse


def oauth_callback(request):
    code = request.GET.get('code')
    if code:
        return HttpResponse(f"OAuth Callback received! Authtorization code: {code}")
    else:
        return HttpResponse("OAuth Callback received, but no authorization code was found in the URL.", status=400)
