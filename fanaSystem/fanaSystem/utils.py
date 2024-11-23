def generic_error_handler(error , errortype = "General Error"):
    return {
        "success": False,
        "error": errortype,
        "message": str(error)
    }