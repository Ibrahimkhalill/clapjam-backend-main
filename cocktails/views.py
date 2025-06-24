from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Cocktail, Ingredient, BookMark
from .serializers import CocktailSerializer, IngredientSerializer, BookMarkSerializer
from .utils.generate_recipe import generate_recipe
# Cocktail Views
@api_view(['GET'])
def cocktail_list(request):
    """List all cocktails or create a new cocktail."""
    if request.method == 'GET':
        cocktails = Cocktail.objects.all()
        serializer = CocktailSerializer(cocktails, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def cocktail_detail(request, pk):
    """Retrieve a single cocktail."""
    try:
        cocktail = Cocktail.objects.get(pk=pk)
    except Cocktail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = CocktailSerializer(cocktail)
    return Response(serializer.data)

@api_view(['POST'])
def cocktail_create(request):
    """Create a new cocktail."""
    serializer = CocktailSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def cocktail_update(request, pk):
    """Update an existing cocktail."""
    try:
        cocktail = Cocktail.objects.get(pk=pk)
    except Cocktail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = CocktailSerializer(cocktail, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def cocktail_delete(request, pk):
    """Delete a cocktail."""
    try:
        cocktail = Cocktail.objects.get(pk=pk)
    except Cocktail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    cocktail.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# BookMark Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bookmark_list(request):
    """List all bookmarks for the authenticated user."""
    bookmarks = BookMark.objects.filter(user=request.user)
    serializer = BookMarkSerializer(bookmarks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bookmark_detail(request, pk):
    """Retrieve a single bookmark for the authenticated user."""
    try:
        bookmark = BookMark.objects.get(pk=pk, user=request.user)
    except BookMark.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = BookMarkSerializer(bookmark)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bookmark_create(request):
    """Create a new bookmark for the authenticated user."""
    serializer = BookMarkSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def bookmark_update(request, pk):
    """Update an existing bookmark for the authenticated user."""
    try:
        bookmark = BookMark.objects.get(pk=pk, user=request.user)
    except BookMark.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = BookMarkSerializer(bookmark, data=request.data, context={'request': request}, partial=True)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bookmark_delete(request, pk):
    """Delete a bookmark for the authenticated user."""
    try:
        bookmark = BookMark.objects.get(pk=pk, user=request.user)
    except BookMark.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    bookmark.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_genarate_receipe_ai(request):
    """
    View to handle POST requests for the alcohol bot.
    Requires authentication.
    """
    if request.method == "POST":
        return generate_recipe(request)
    return Response({"success": False, "error": "Method not allowed"}, status=405)