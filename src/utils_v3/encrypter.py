#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# technical
import string
import secrets


# configs
Strong_Password_Characters_Pool = \
    string.ascii_letters + \
    string.digits + \
    string.punctuation



def get_strong_password(length=30):

    strong_password = ''.join(
        secrets.choice(Strong_Password_Characters_Pool)
        for i in range(length)
    )

    return strong_password
