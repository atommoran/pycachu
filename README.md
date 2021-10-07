# Pycachu

An interactive cache that saves user-submitted credentials and tokens in a yaml file, and passwords in the OS keychain using the keyring module

## Getting Started

Once you have imported the module:
```
import pycachu
```

You can create a cache. This should always be the first step.

```
cache = pycachu.Cache("file_name")
```

This will create a yaml file with the specified name. The file will be created at your current directory location by default, but you can specify a path also:

```
cache = pycachu.Cache("file_name", path="~/")
```

NOTE: The trialing / is not added for you,make sure to include it on the path.

## Getting a token

When you wish to grab a token, just use the following:

```
token = cache.get_token("key")
```

The token will be requested by the user at runtime then saved to the cache yaml file. On running a second time, the token will be grabbed directly from the cache with no user input.

This creates a Token object. You can grab the token with .token

```
print(token.token)
```

You can specify your own terminal output for the user, and hide the user input:

```
token = pycachu.Token(cache, "key", user_prompt="Submit the token: ", hide_input=True)
```

All kwargs to the Token initiator are carried in Cache.get_token(). This is just a demonstration of the other (more convoluted) method for creating a Token.

## Getting a credential

When you wish to grab a credential, just use the following:

```
credential = cache.get_credential("key")
```

The user will then be asked for the username and password, if already not saved in the cache. The password will be stored in the OS keychain using Keyring.

This creates a Credential object. You can grab the credentials with .username and .password.

```
print(credential.username, credential.password)
```

You can specify your own terminal output for the name and password, and hide the username input (the password input is hidden by default):

```
credential = pycachu.Credential(cache, "key", username_prompt="Submit the username: ", password_prompt="And now the password: ", hide_username=True, hide_password=False)
```

All kwargs to the Credential initiator are carried in Cache.get_credential(). This is just a demonstration of the other (more convoluted) method for creating a Credential.

## Oh no! My token/credential didn't work

Raise a cache error to remove the cache object from the cache

```
token1.error()
raise pycachu.CacheTokenError(token2)

credential1.error()
raise pycachu.CacheCredentialError(credential2)
```

This will raise an exception and also remove the token/credential from the cache to be re-entered on next runtime.

If you don't want to raise an Exception, both object have a remove() function:

```
token.remove()
credential.remove()
```

## Validators

Validators are also imported, these are used to match the input to a set regular expression. By default all inputs use the `pycachu.validators.NotEmpty()` but you can specify any of the other validators, or create your own Validator class.