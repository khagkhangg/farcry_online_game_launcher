from django.db import models


# Create your models here.
class Player(models.Model):
    """ Model that store all player's informations, including their settings
    and character selected.
    """

    player_name = models.CharField(max_length=256, unique=True)
    player_email = models.CharField(max_length=256)
    player_password = models.CharField(max_length=256)
    # Check if player has verified their email address
    player_verified = models.BooleanField(default=False)
    # Store player's newest character options
    player_character_model = models.CharField(max_length=256, default="new")
    player_character_color = models.CharField(max_length=256, default="new")
    # Store player's newest key bindings
    player_key_bindings = models.TextField(default="new")

    def __str__(self):
        # Player is defined by their name
        return str(self.player_name)


class Match(models.Model):
    """ Model that store all match's information,
    """
    match_name = models.CharField(max_length=256, unique=True, default="match")
    match_start_time = models.CharField(max_length=256)
    match_end_time = models.CharField(max_length=256)
    # List of frags
    match_frags = models.TextField()

    def __str__(self):
        # Match is defined by it's start time
        return str(self.match_name)


class LoginToken(models.Model):
    """ Model that store a token using for authenticating a player,
    """
    token = models.TextField()
    player_name = models.ForeignKey(Player, on_delete=models.CASCADE)
    one_time_token = models.BooleanField(default=False)

    def __str__(self):
        # Token is defined by player name
        return str(self.player_name)


class VerifyToken(models.Model):
    """ Model that store a token using for verifying a player's mail,
    """
    token = models.TextField()
    player_name = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        # Token is defined by player name
        return str(self.player_name)
