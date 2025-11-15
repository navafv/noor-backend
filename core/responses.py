from rest_framework.response import Response

def success(data=None, message="", status=200):
    return Response({"success": True, "message": message, "data": data}, status=status)

def error(message="", details=None, status=400):
    return Response({"success": False, "message": message, "error": details}, status=status)
