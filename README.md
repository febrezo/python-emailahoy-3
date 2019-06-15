Python Email Ahoy 3
====================

**A Python email utility that verifies existence of an email address**


Overview
========

A Python email utility that verifies existence of an email address.
This package is based on [this](https://github.com/un33k/python-emailahoy) package which only run in Python 2.
It has been refactored to work in Python 3.

How to install
==================

Use Pip (note that it works only for Python 3.6+ sicne it uses f-strings):

```
pip3 install python-emailahoy3 --user
```

How to use
=================

Use the shorthand function for quick check:

```
from emailahoy3 import verify_email_address
status =verify_email_address('test@example.com')
print(status)
```

Codes are defined as follows:
- `1`. The email exists.
- `0`. The email does not exist.
- `-1`. The existence of the email could not be verified.

You can also use the class for more control & more granular return status:

```
from emailahoy3 import VerifyEmail
e = VerifyEmail()
status = e.verify_email_smtp(
                    email='test@example.com',
                    from_host='mydomain.com',
                    from_email='verify@mydomain.com'
                )
if e.was_found(status):
    print >> sys.stderr, "Found:", status
elif e.not_found(status):
    print >> sys.stderr, "Not Found:", status
else:
    print >> sys.stderr, "Unverifiable:", status
```



Notes
=================

1. Not all email servers will return the correct status
2. Checking an invalid email address returns within 1 second
3. Checking a valid email address returns within 4 seconds or more

Running the tests
=================

To run the tests against the current environment:

```
python3 -m unittest discover
```

License
====================

Released under a ([BSD](LICENSE.md)) license.
