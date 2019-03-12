"""This is module Doc String"""


def example_func():
    """
    # Description

    Bla bal bla

    # Arguments

    |-----------|------|-------------|
    | Attribute | Type | Description | 
    | name      | String |

    # Example

    ```python
    example_func(
        name = "example",
        srcs = ["bla", "bla",],
    )
    ```
    """
    pass


"""LPP configuration

This module defines default values for lpp_config() macro.
See also: lpp.bzl
"""


DEFAULT_DSPS_CONFIG = (select({
    "@lpp//:trinity": ["dsps=65"],
    "@lpp//:lynx": ["dsps=176"],
    "@lpp//:eagleowl": ["dsps=144"],
}) + [
    "snid=0",
    "dsp0: spark=true",
])
"""Default DSPs configuration

lpp_config(dsps=DEFAULT_DSPS_CONFIG)

Parameters:
    dsps       - Number of DSPs available on EMCA.
                 Default value depends on EMCA type.
    max_sparks - LPP will automatically change DSPs into SPARKs when needed,
                 max_sparks limits the maximum number of sparks in a build.
                 Default value is 'dsps - 1'.
    snid       - SubNode ID.
                 Default is 0.
    dspX:      - DSP X configuration:
    dspX:spark - Is DSP "spark" or not.
                 Values: true or false.
                 Default is false.
    dspX:debug - For test and debug sessions in a simulated environment,
                 would not work on real HW.
                 Equivalent to DEBUG64KLDM DSP type.
                 Sets LPM size to 0x100000 words
                 and LDM size to 0x10000 words.
                 Values: true or false.
                 Default is false.
Example:
lpp_config(
    dsps = [
        "dsps=5",
        "max_sparks=3",
        "snid=3",
        "dsp0: spark=true, debug=true",
        "dsp1: debug=true",
    ],
)
"""
