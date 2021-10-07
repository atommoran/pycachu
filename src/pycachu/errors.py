#!/usr/bin/env python

class CacheLoadError(Exception):
    pass

class CacheObjectError(Exception):
    "Exception for when a cache object fails that removes the object and then raises the error"
    def __init__(self, object, explanation="", object_type=""):
        object.remove()
        self.file = object.cache.file_name
        self.key = object.key
        self.object_type = object_type
        if explanation != "":
            self.explanation = explanation
        else:
            self.explanation = f"{self.object_type} error raised"
        self.message = f"{self.object_type} {self.key} in cache {self.file}: {self.explanation}"
        super().__init__(self.message)

class CacheTokenError(CacheObjectError):
    "Exception for when a token fails that tidies up the token while raising error"
    def __init__(self, token, explanation=""):
        super().__init__(token, explanation=explanation, object_type="Token")

class CacheCredentialError(CacheObjectError):
    "Exception for when a credential fails that tidies up the credential while raising error"
    def __init__(self, credential, explanation=""):
        super().__init__(credential, explanation=explanation, object_type="Credential")
