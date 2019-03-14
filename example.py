"""
This is module Doc String
1
2
3
"""


def simple_func():
    """Simple description"""
    pass


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


DEFAULT_CONFIG = (select({
    "@main//:one": ["number=1"],
    "@main//:two": ["number=2"],
}) + [
    "id=0",
])
"""Default configuration

```
config(conf=DEFAULT_CONFIG)
```

## Parameters:

    number     - Number.
                 Default value depends.
    id         - ID.

## Example:

```
lpp_config(
    dsps = [
        "dsps=5",
        "max_sparks=3",
        "snid=3",
        "dsp0: spark=true, debug=true",
        "dsp1: debug=true",
    ],
)
```
"""
