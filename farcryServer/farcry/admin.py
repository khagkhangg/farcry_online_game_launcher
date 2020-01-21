from django.contrib import admin

# Register your models here.
from .models import Player, Match, LoginToken, VerifyToken


admin.site.register(Player)
admin.site.register(Match)
admin.site.register(LoginToken)
admin.site.register(VerifyToken)
