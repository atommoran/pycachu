#!/usr/bin/env python

import os
import keyring
import yaml


def _generate_keyring_key(file_location, key):
    file_key_part = file_location.replace("/", "_")
    file_key_part = file_location.replace("\\", "_")
    keyring_key = f"{file_key_part}.{key}"
    return keyring_key


class Token:
    def _get_token_from_user(self, prompt=None):
        if prompt is None:
            return input(
                f"Please input the token for {self.key} in the {self.cache.file_name} cache: "
            )
        else:
            return input(prompt)

    def __init__(self, cache, key, user_prompt=None):
        self.cache = cache
        self.key = key
        if key not in cache.tokens:
            self.token = self._get_token_from_user(prompt=user_prompt)
            self.cache.tokens[key] = self.token
            self.cache._write()
        else:
            self.token = cache.tokens[key]

    def reset(self, new_token):
        self.cache.tokens[self.key] = new_token
        self.cache._write()

    def remove(self):
        del self.cache.tokens[self.key]
        self.cache._write()


class Credential:
    def _get_username_from_user(self, prompt=None):
        if prompt is None:
            return input(
                f"Please input the username for {self.key} in the {self.cache.file_name} cache: "
            )
        else:
            return input(prompt)

    def _get_password_from_user(self, prompt=None):
        if prompt is None:
            return input(
                f"Please input the password for {self.key} in the {self.cache.file_name} cache: "
            )
        else:
            return input(prompt)

    def __init__(self, cache, key, username_prompt=None, password_prompt=None):
        self.cache = cache
        self.key = key
        self.keyring_key = _generate_keyring_key(cache.file_location, key)
        if key not in cache.credentials:
            self.username = self._get_username_from_user(prompt=username_prompt)
            self.cache.credentials[key] = self.username
            self.cache._write()
        else:
            self.username = cache.credentials[key]

        self.password = keyring.get_password(self.keyring_key, self.username)
        if self.password is None:
            self.password = self._get_password_from_user(prompt=password_prompt)
            keyring.set_password(self.keyring_key, self.username, self.password)

    def reset_password(self, password_prompt=None):
        self.password = self._get_password_from_user(prompt=password_prompt)
        keyring.set_password(self.keyring_key, self.username, self.password)

    def reset(self, username_prompt=None, password_prompt=None):
        keyring.delete_password(self.keyring_key, self.username)
        self.username = self._get_username_from_user(prompt=username_prompt)
        self.cache.credentials[self.key] = self.username
        self.cache._write()
        self.password = self._get_password_from_user(prompt=password_prompt)
        keyring.set_password(self.keyring_key, self.username, self.password)

    def remove_password(self):
        keyring.delete_password(self.keyring_key, self.username)

    def remove(self):
        self.remove_password()
        del self.cache.credentials[self.key]
        self.cache._write()


class Cache:
    def __init__(self, file_name, path="", reset=False):
        self.file_name = file_name
        self.file_path = path
        self.file_location = f"{path}/{file_name}"

        if reset == True and os.path.isfile(self.file_location):
            self.file = open(self.file_location, "w")
            self._load()
            self.clear()
            self._create()
        elif os.path.isfile(self.file_location):
            self.file = open(self.file_location, "w")
            self._load()
        else:
            self.file = open(self.file_location, "w")
            self._create()

    def __del__(self):
        self.file.close()

    def _write(self):
        yaml.dump(self.full_dict, self.file, default_flow_style=False)

    def _create(self):
        self.tokens = {}
        self.credentials = {}
        self.full_dict = {"tokens": self.tokens, "credentials": self.credentials}
        self._write()

    def _validate_base_key(self, key):
        if key not in self.full_dict:
            raise Exception()  # This will get replaced with a homemade error
        if not isinstance(self.full_dict[key], dict):
            raise Exception()  # This will get replaced with a homemade error

    def _validate(self):
        if not hasattr(self, "full_dict"):
            raise Exception()  # This will get replaced with a homemade error
        self._validate_base_key("tokens")
        self._validate_base_key("credentials")

    def _load(self):
        self.full_dict = yaml.safe_load(self.file)
        self._validate()
        self.tokens = self.full_dict["tokens"]
        self.credentials = self.full_dict["credentials"]
        self.full_dict = {"tokens": self.tokens, "credentials": self.credentials}

    def get_token(self, key, user_prompt=None):
        return Token(self, key, user_prompt=user_prompt)

    def get_credential(self, key, username_prompt=None, password_prompt=None):
        return Credential(
            self, key, username_prompt=username_prompt, password_prompt=password_prompt
        )

    def clear_credentials(self):
        for key in self.credentials:
            keyring.delete_password(
                _generate_keyring_key(self.file_location, key), self.credentials[key]
            )
        self.credentials = {}
        self._write()

    def clear_tokens(self):
        self.tokens = {}
        self._write()

    def clear(self):
        self.clear_credentials()
        self.clear_tokens()
