from django.shortcuts import redirect


def root_landing(request):
    if request.user.is_authenticated:
        return redirect("/chat/")
    return redirect("/login/")
