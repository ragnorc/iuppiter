import re


def validate_zipcode(zipcode):
    '''Does nothing if zipcode is semantically and syntactically as expected,
        raises AssertionError otherwise '''

    if not isinstance(zipcode, str):
        zipcode = str(zipcode)

    assert isinstance(zipcode, str)

    assert re.match(r"([0]{1}[1-9]{1}|[1-9]{1}[0-9]{1})[0-9]{3}",
                    zipcode)  # checks if zipcode is semantically correct
    assert len(zipcode) == 5  # zipcodes in Germany have exactly 5 digits


def validate_consumption(consumption):
    '''Does nothing if consumption is semantically and syntactically as
     expected, raises AssertionError otherwise  '''
    if not isinstance(consumption, str):
        consumption = str(consumption)

    assert isinstance(consumption, str)

    # minimum consumption that is required by check24
    assert int(consumption) >= 100
