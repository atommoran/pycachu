#!/usr/bin/env python

import os
import keyring
import yaml
from getpass import getpass

from src.pycachu.errors import *
import src.pycachu.validators as validators


def _generate_keyring_key(file_location, key):
    file_key_part = file_location.replace("/", "_")
    file_key_part = file_location.replace("\\", "_")
    keyring_key = f"{file_key_part}.{key}"
    return keyring_key


def get_input(prompt, hide=False):
    if hide == True:
        return getpass(prompt)
    elif hide == False:
        return input(prompt)
    else:
        raise SyntaxError("get_input: hide paramter must be True or False")


class Token:
    def _get_token_from_user(self):
        if self.user_prompt is None:
            inputted = get_input(
                f"Please input the token for {self.key} in the {self.cache.file_name} cache: ",
                hide=self.hide_input,
            )
        else:
            inputted = get_input(self.user_prompt, hide=self.hide_input)
        while not self.validator.validate(inputted):
            inputted = get_input(
                f"The token was invalid ({self.validator.message}). Try again: ",
                hide=self.hide_input,
            )
        return inputted

    def __init__(
        self,
        cache,
        key,
        user_prompt=None,
        hide_input=False,
        validator=validators.NotEmpty(),
    ):
        self.cache = cache
        self.key = key
        self.user_prompt = user_prompt
        self.hide_input = hide_input
        self.validator = validator
        if key not in cache.tokens:
            self.token = self._get_token_from_user()
            self.cache.tokens[key] = self.token
            self.cache._write()
        else:
            self.token = cache.tokens[key]

    def reset(self, user_prompt=None):
        if user_prompt is not None:
            self.user_prompt = user_prompt
        new_token = self._get_token_from_user()
        self.token = new_token
        self.cache.tokens[self.key] = new_token
        self.cache._write()

    def remove(self):
        del self.cache.tokens[self.key]
        self.cache._write()

    def error(self, **kwargs):
        raise CacheTokenError(self, **kwargs)


class Credential:
    def _get_username_from_user(self):
        if self.username_prompt is None:
            username = get_input(
                f"Please input the username for {self.key} in the {self.cache.file_name} cache: ",
                hide=self.hide_username,
            )
        else:
            username = get_input(self.username_prompt, hide=self.hide_username)
        while not self.username_validator.validate(username):
            username = get_input(
                f"The username was invalid ({self.username_validator.message}). Try again: ",
                hide=self.hide_username,
            )
        return username

    def _get_password_from_user(self):
        if self.password_prompt is None:
            password = get_input(
                f"Please input the password for {self.key} in the {self.cache.file_name} cache: ",
                hide=self.hide_password,
            )
        else:
            password = get_input(self.password_prompt, hide=self.hide_password)
        while not self.password_validator.validate(password):
            password = get_input(
                f"The password was invalid ({self.password_validator.message}). Try again: ",
                hide=self.hide_password,
            )
        return password

    def __init__(
        self,
        cache,
        key,
        username_prompt=None,
        password_prompt=None,
        hide_username=False,
        hide_password=True,
        username_validator=validators.NotEmpty(),
        password_validator=validators.NotEmpty(),
    ):
        self.cache = cache
        self.key = key
        self.username_prompt = username_prompt
        self.password_prompt = password_prompt
        self.hide_username = hide_username
        self.hide_password = hide_password
        self.keyring_key = _generate_keyring_key(cache.file_location, key)
        self.username_validator = username_validator
        self.password_validator = password_validator
        if key not in cache.credentials:
            self.username = self._get_username_from_user()
            self.cache.credentials[key] = self.username
            self.cache._write()
        else:
            self.username = cache.credentials[key]

        self.password = keyring.get_password(self.keyring_key, self.username)
        if self.password is None:
            self.password = self._get_password_from_user()
            keyring.set_password(self.keyring_key, self.username, self.password)

    def reset_password(self, password_prompt=None):
        if password_prompt is not None:
            self.password_prompt = password_prompt
        self.password = self._get_password_from_user()
        keyring.set_password(self.keyring_key, self.username, self.password)

    def reset(self, username_prompt=None, password_prompt=None):
        if username_prompt is not None:
            self.username_prompt = username_prompt
        if password_prompt is not None:
            self.password_prompt = password_prompt
        keyring.delete_password(self.keyring_key, self.username)
        self.username = self._get_username_from_user(prompt=username_prompt)
        self.cache.credentials[self.key] = self.username
        self.cache._write()
        self.password = self._get_password_from_user()
        keyring.set_password(self.keyring_key, self.username, self.password)

    def remove_password(self):
        keyring.delete_password(self.keyring_key, self.username)

    def remove(self):
        self.remove_password()
        del self.cache.credentials[self.key]
        self.cache._write()

    def error(self, **kwargs):
        raise CacheCredentialError(self, **kwargs)


class Cache:
    def __init__(self, file_name, path="", reset=False):
        self.file_name = file_name
        self.file_path = path
        self.file_location = f"{path}{file_name}"

        if reset == True and os.path.isfile(
            self.file_location
        ):  # file exists, but we're resetting it
            self._load()
            self.clear()
            self._create()
        elif (
            os.path.isfile(self.file_location)
            and os.path.getsize(self.file_location) == 0
        ):  # file exists, but is empty
            self._create()
        elif os.path.isfile(
            self.file_location
        ):  # file exists and is good to be loaded up
            self._load()
        else:  # file does not exist
            self._create()

    def _write(self):
        with open(self.file_location, "w") as cache_file:
            yaml.dump(self.full_dict, cache_file, default_flow_style=False)

    def _create(self):
        self.tokens = {}
        self.credentials = {}
        self.full_dict = {"tokens": self.tokens, "credentials": self.credentials}
        self._write()

    def _validate_base_key(self, key):
        if key not in self.full_dict:
            raise KeyError(f"Did not find {key} in the YAML from {self.file_name}")
        if not isinstance(self.full_dict[key], dict):
            raise TypeError(
                f"{key} in the YAML from {self.file_name} is not in the expected key-value format"
            )

    def _validate_dict(self):
        if not hasattr(self, "full_dict"):
            raise CacheLoadError(f"No YAML was loaded from {self.file_name}")
        if not isinstance(self.full_dict, dict):
            raise CacheLoadError(
                f"The YAML from {self.file_name} was not in the expected key-value format"
            )
        self._validate_base_key("tokens")
        self._validate_base_key("credentials")

    def _load(self):
        with open(self.file_location, "r") as cache_file:
            try:
                self.full_dict = yaml.safe_load(cache_file)
            except:
                raise CacheLoadError(
                    f"Valid YAML could not be safe-loaded from {self.file_name}"
                )
        self._validate_dict()
        self.tokens = self.full_dict["tokens"]
        self.credentials = self.full_dict["credentials"]
        self.full_dict = {"tokens": self.tokens, "credentials": self.credentials}

    def get_token(self, key, **kwargs):
        return Token(self, key, **kwargs)

    def get_credential(self, key, **kwargs):
        return Credential(self, key, **kwargs)

    def clear_credentials(self):
        for key in self.credentials:
            if (
                keyring.get_password(
                    _generate_keyring_key(self.file_location, key),
                    self.credentials[key],
                )
                != None
            ):
                keyring.delete_password(
                    _generate_keyring_key(self.file_location, key),
                    self.credentials[key],
                )
        self.credentials.clear()
        self._write()

    def clear_tokens(self):
        self.tokens.clear()
        self._write()

    def clear(self):
        self.clear_credentials()
        self.clear_tokens()
