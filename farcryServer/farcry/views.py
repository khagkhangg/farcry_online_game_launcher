from django.shortcuts import render
from rest_framework import viewsets
from .models import Player, Match, LoginToken, VerifyToken
from django.http import HttpResponseRedirect
# libraries for restfulAPI
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_202_ACCEPTED,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.response import Response
# libraries for authentication steps
from jwt import encode
from datetime import datetime
# libraries for hashing
from hashlib import md5
from .send_email_from_gmail import send_mail


def request_is_valid(items):
    """
    Check if request have all necessary params, header, body
    """
    for item in items:
        if not item:
            return False
    return True


def is_registered(item, item_type):
    list_items = Player.objects.values_list(item_type, flat=True)
    # Check if email has been already used
    if item in list_items:
        return Response({'error': '{} is already taken! Please try another.'.format(item_type)},
                        status=HTTP_406_NOT_ACCEPTABLE)
    else:
        return Response({'OK': 'Valid for new registration',},
                        status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def check_player_name(request):
    """
    Check email/ username availability
    """
    # Get string fields from params
    player_name = request.GET.get("player_name")

    if not player_name:
        return Response({'error': 'Player_name is missing! Please verify your request.'},
                        status=HTTP_400_BAD_REQUEST)

    return is_registered(player_name, 'player_name')


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def check_email(request):
    """
    Check email availability
    """
    # Get string fields from params
    player_email = request.GET.get("player_email")

    if not player_email:
        return Response({'error': 'Player_email is missing! Please verify your request.'},
                        status=HTTP_400_BAD_REQUEST)

    return is_registered(player_email, 'player_email')


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def check_availability(request):
    """
    Check email/ username availability
    """
    # Get string fields from params
    player_name = request.GET.get("player_name")
    player_email = request.GET.get("player_email")

    if not request_is_valid([player_name, player_email]):
        return Response({'error': 'Some params are missing! Please verify your request.'},
                        status=HTTP_400_BAD_REQUEST)

    list_email = Player.objects.values_list('player_email', flat=True)
    # Check if email has been already used
    if player_email in list_email:
        return Response({'error': 'Email is already taken! Please try another.'},
                        status=HTTP_406_NOT_ACCEPTABLE)
    try:
        # Check user existence
        exist_name = Player.objects.get(player_name=player_name).player_name
        return Response({'error': 'Username is already taken! Please try another.'},
                        status=HTTP_406_NOT_ACCEPTABLE)
    except Player.DoesNotExist:
        return Response({'OK': 'This account is valid for new registration',},
                        status=HTTP_200_OK)


def generate_token(player_name, is_one_time_token=False, is_verify_token=False):
    # Generate token for this user, using current time as a secret
    payload = {'player_name':player_name}
    secret = str(datetime.now())
    token = encode(payload, secret, algorithm='HS256').decode('utf-8')
    # Overwrite or create token to databse
    if not is_verify_token:
        LoginToken.objects.update_or_create(player_name=player_name, defaults={'player_name':player_name, 'token': token, 'one_time_token': is_one_time_token})
    else:
        VerifyToken.objects.create(player_name=player_name, token= token)
    return token


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def verify(request):
    """
    Control verification of user via email
    """
    # Get string fields from params
    player_name = request.GET.get("player_name")
    token = request.GET.get("one_time_token")

    # Only authenticated users are able to verify their own account
    try:
        if authenticate_by_token(token, player_name, True):
            # Verify user
            player = Player.objects.filter(player_name=player_name)
            player.update(player_verified=True)
            VerifyToken.objects.filter(player_name=player_name).delete()
            return HttpResponseRedirect('/farcryAPI/v1/redirect/verification_success/')
        else:
            # Reject unauthenticated user
            return HttpResponseRedirect('/farcryAPI/v1/redirect/verification_failure/')
    except Player.DoesNotExist:
        # User not exist (rarely happend)
        return HttpResponseRedirect('/farcryAPI/v1/redirect/verification_failure/')


@csrf_exempt
@api_view(["PUT"])
@permission_classes((AllowAny,))
def update(request):
    """
    Update user preferences
    """
    # Get string fields from userinput
    player_character_model = request.data.get("player_character_model")
    player_character_color = request.data.get("player_character_color")
    player_key_bindings = request.data.get("player_key_bindings")

    if not request_is_valid([player_character_model, player_character_color, player_key_bindings]):
        return Response({'error': 'Some params are missing! Please verify your request.'},
                        status=HTTP_400_BAD_REQUEST)

    # Get string fields from params
    player_name = request.GET.get("player_name")
    # Get authorizaion field from header
    token = request.META.get('HTTP_AUTHORIZATION')

    # Only authenticated users are able to update their own account
    try:
        if authenticate_by_token(token, player_name):
            # Update account with new preferences
            player = Player.objects.filter(player_name=player_name)
            player.update(player_character_model=player_character_model, player_character_color=player_character_color,
                          player_key_bindings=player_key_bindings)
            return Response({'sucess': 'New preferences saved!'},
                            status=HTTP_200_OK)
        else:
            # Reject unauthenticated user
            return Response({'error': 'No permission! Please log in!'},
                            status=HTTP_406_NOT_ACCEPTABLE)
    except Player.DoesNotExist:
        # Reject unauthenticated user
        return Response({'error': 'No permission! Please log in!'},
                        status=HTTP_406_NOT_ACCEPTABLE)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def submit(request):
    """
    Control match submit request
    """

    # Get string fields from body
    match_name = request.data.get("match_name")
    match_start_time = request.data.get("match_start_time")
    match_end_time = request.data.get("match_end_time")
    match_frags = request.data.get("match_frags")


    if not request_is_valid([match_name, match_start_time, match_end_time, match_frags]):
        return Response({'error': 'Some params are missing! Please verify your request.'},
                        status=HTTP_400_BAD_REQUEST)

    # Get field from params
    player_name = request.GET.get("player_name")

    # Get authorizaion field from header
    token = request.META.get('HTTP_AUTHORIZATION')

    # Get a list of matches
    list_match = Match.objects.values_list('match_name', flat=True)

    # Check match existence
    if match_name in list_match:
        return Response({'error': 'Match log was aready stored!'},
                        status=HTTP_406_NOT_ACCEPTABLE)

    # Only authenticated users are able to submit matches
    if authenticate_by_token(token, player_name):
        # Create and store match instance in database
        Match.objects.create(match_name=match_name, match_start_time=match_start_time,
                             match_end_time=match_end_time, match_frags=match_frags)
        return Response({'sucess': 'Match log has been saved succesfully!'},
                        status=HTTP_200_OK)
    else:
        # Reject unauthenticated users
        return Response({'error': 'No permission! Please log in!'},
                        status=HTTP_401_UNAUTHORIZED)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def register(request):
    """
    Control register request
    """
    # Get string fields from body
    player_name = request.data.get("player_name")
    player_email = request.data.get("player_email")
    player_password = request.data.get("player_password")

    if not request_is_valid([player_name, player_email, player_password]):
        return Response({'error': 'Some params are missing! Please verify your request.'},
                        status=HTTP_400_BAD_REQUEST)

    # Get list of emails
    list_email = Player.objects.values_list('player_email', flat=True)
    hashed_player_password = md5(player_password.encode('utf-8')).hexdigest()
    # Check if email has been already used
    if player_email in list_email:
        return Response({'error': 'Email is already taken! Please try another.'},
                        status=HTTP_406_NOT_ACCEPTABLE)
    try:
        # Check user existence
        exist_name = Player.objects.get(player_name=player_name).player_name
        return Response({'error': 'Username is already taken! Please try another.'},
                        status=HTTP_406_NOT_ACCEPTABLE)
    except Player.DoesNotExist:
        # Create new user
        Player.objects.create(player_name=player_name, player_email=player_email, player_password=hashed_player_password, player_key_bindings="new")
        # Genare token for verify purpose
        # Verify link format: http://127.0.0.1:8000/farcryAPI/v1/users/login/?player_name=<playername>&one_time_token=<playername>
        login_token = generate_token(player_name, True)
        verify_token = generate_token(player_name, False, True)
        verify_link = 'Click here to verify your account on Farcry Online: https://farcryserver.herokuapp.com/farcryAPI/v1/players/verify/?player_name={}&one_time_token={}'.format(player_name, verify_token)
        send_mail(verify_link, player_email)
        return Response({'sucess': 'Account created succesfully! Please verify your email before login', 'token': login_token},
                        status=HTTP_202_ACCEPTED)


def authenticate_by_password(player_name, player_password):
    """
    Check if username and password match each other
    """
    try:
        hashed_player_password = md5(player_password.encode('utf-8')).hexdigest()
        user = Player.objects.get(player_name=player_name)
        # check if user input valid password
        if hashed_player_password == user.player_password:
            return user
    except Player.DoesNotExist:
        return None


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    """
    Control login request, return a token if succesfully run
    """
    # Get string fields from body
    userinput = request.data.get("player_name")
    player_password = request.data.get("player_password")

    if not request_is_valid([userinput, player_password]):
        return Response({'error': 'Some params are missing! Please verify your request.'},
                        status=HTTP_400_BAD_REQUEST)

    try:
        # When user input an email, try to get player_name
        player_name = Player.objects.get(player_email=userinput).player_name
    except Player.DoesNotExist:
        # Otherwise
        player_name = userinput
    # Authenticate player_name/ password
    if not authenticate_by_password(player_name, player_password) and not authenticate_by_token(player_password, player_name, True):
        # player_name/ password is not correct
        return Response({'error': 'Username or password is not corrected!'},
                        status=HTTP_404_NOT_FOUND)
    elif not Player.objects.get(player_name=player_name).player_verified:
        # Email not verified
        token = generate_token(player_name, True)
        return Response({'error': 'Please verified your email!',
                         'token': token},
                        status=HTTP_406_NOT_ACCEPTABLE)

    token = generate_token(player_name)
    # Get data from database in order to return to the client
    player_object = Player.objects.get(player_name=player_name)
    true_player_name = player_object.player_name
    player_character_model = player_object.player_character_model
    player_character_color = player_object.player_character_color
    player_key_bindings = player_object.player_key_bindings

    # Success response
    return Response({'token': token, 'player_name': true_player_name, 'player_character_model':player_character_model,
                     'player_character_color':player_character_color, 'player_key_bindings':player_key_bindings},
                    status=HTTP_200_OK)


def authenticate_by_token(token, player_name, is_one_time_token=False):
    """
    Check if username and tokens match each other
    """
    try:
        user = LoginToken.objects.get(player_name=player_name)
        if player_name in VerifyToken.objects.values_list('player_name', flat=True):
            verify_user = VerifyToken.objects.get(player_name=player_name)
            if token == verify_user.token:
                return True

        # check if user input valid token
        if token == user.token and not user.one_time_token:
            return True
        elif is_one_time_token and token == user.token and user.one_time_token:
            return True
    except LoginToken.DoesNotExist:
        return False


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def logout(request):
    """
    Control logout request, return logout message
    """
    # Get string fields from params
    player_name = request.GET.get("player_name")
    # Get authorizaion field from header
    token = request.META.get('HTTP_AUTHORIZATION')

    if not request_is_valid([player_name, token]):
        return Response({'error': 'Some params are missing! Please verify your request.'},
                        status=HTTP_400_BAD_REQUEST)

    if authenticate_by_token(token, player_name):
        # Remove token from database
        LoginToken.objects.filter(player_name=player_name).delete()
        # Success response
        return Response({'success': 'Log out succesfully!'},
                        status=HTTP_200_OK)
    else:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)


def verification_success(request):
    context = {}
    return render(request, 'farcry/verification_success.html', context)


def verification_failure(request):
    context = {}
    return render(request, 'farcry/verification_failure.html', context)
