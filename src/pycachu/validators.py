#!/usr/bin/env python

import re


class Validator:
    def __init__(self):
        self.regex = "*"
        self.message = "Base validator that allows anything"

    def validate(self, string):
        match = re.fullmatch(self.regex, string)
        if match is not None:
            return True
        else:
            return False

    def get_message(self):
        return self.message


class NotEmpty(Validator):
    def __init__(self):
        self.regex = "^(?!\s*$).+"
        self.message = "Must not be empty string"


class Email(Validator):
    def __init__(self):
        self.regex = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
        self.message = "Must be email"


class Password(Validator):
    def __init__(
        self,
        uppercase=True,
        lowercase=True,
        number=True,
        special_char=True,
        length=8,
        at_least=True,
    ):
        if uppercase == lowercase == special_char == number == False:
            if at_least:
                self.regex = f"^.{{{length},}}$"
                self.message = "Must be of length {length} at least"
            else:
                self.regex = f"^.{{{length}}}$"
                self.message = "Must be of length {length}"
        else:
            self.regex = "^"
            self.message = "Must include "
            if uppercase:
                self.regex += "(?=.*[a-z])"
                self.message += "a lowercase letter, "
            if uppercase:
                self.regex += "(?=.*[A-Z])"
                self.message += "an uppercase letter, "
            if number:
                self.regex += "(?=.*[0-9])"
                self.message += "a number, "
            if special_char:
                self.regex += "(?=.*[!@#$&*£^,.])"
                self.message += "a special character, "
            if at_least:
                self.regex += f".{{{length},}}$"
                self.message += f"and must be at least {length} characters long"
            else:
                self.regex += f".{{{length}}}$"
                self.message += f"and must be {length} characters long"


class Length(Password):
    def __init__(self, length=8, at_least=False):
        super().__init__(
            uppercase=False,
            lowercase=False,
            number=False,
            special_char=False,
            length=length,
            at_least=at_least,
        )
