"""
Functions for working with contract ABIs.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Sequence, Tuple, Union, cast

from eth_typing.abi import (
    ABI,
    ABIComponent,
    ABIFunction,
)
from web3 import Web3


def find_abi_constructor(abi: ABI) -> ABIFunction:
    """
    Given an ABI and function name, find the ABIFunction element.
    """

    for element in abi:
        if element["type"] == "constructor" and "name" not in element:
            return cast(ABIFunction, element)

    raise ValueError("constructor not found in ABI")


def find_abi_function(abi: ABI, function_name: str) -> ABIFunction:
    """
    Given an ABI and function name, find the ABIFunction element.
    """

    for element in abi:
        if element["type"] == "function" and element["name"] == function_name:
            return element

    raise ValueError(f"function {function_name} not found in ABI")


def parse_arguments(abi_function: ABIFunction, arguments: List[str]) -> List[Any]:
    """
    Given an ABI, a function name and a list of string parameters,
    parse the parameters to suitable types to call the function on a
    contract with the given ABI.
    """

    if inputs := abi_function.get("inputs"):
        parsers = _argument_parsers_for_params(inputs)
        if len(parsers) != len(arguments):
            raise ValueError(
                f"function requires {len(parsers)}, received {len(arguments)}"
            )

        return [parse(arg) for parse, arg in zip(parsers, arguments)]
    return []


def parse_return_value(abi_function: ABIFunction, return_value: Any) -> Any:
    """
    Given the function ABI and the return values, matches the return values
    with their names from the ABI spec.

    Supports void types, and flattening a one-element tuple to a raw type.
    """

    outputs = abi_function.get("outputs")
    if not outputs:
        return None

    if len(outputs) == 1:
        # Single return value (including an array)
        return _parse_return_value_from_type(
            outputs[0]["type"], outputs[0], return_value
        )

    return_value_tuple = tuple(return_value)
    return _parse_return_value_tuple(outputs, return_value_tuple)


ParamType = Union[str, int, float, bool]
"""
A native type which can be passed as an argument to a ContractFunction
"""

ParamParser = Callable[[str], ParamType]
"""
Function to parse a string to a ParamType
"""


def _parse_string(value: str) -> str:
    """
    Identity parser.
    """
    return value


def _parse_bool(bool_str: str) -> bool:
    """
    Boolean parser.
    """
    if bool_str in ["False", "false", "0", ""]:
        return False

    return True


def _parse_complex(value: str) -> Any:
    """
    Parse a complex type, such as an array or tuple.
    """
    return json.loads(value)


def _string_to_argument_fn_for_type(arg_type: str) -> ParamParser:
    """
    Return a function which parses a string into a type suitable for
    function arguments.
    """
    if arg_type.endswith("[]") or arg_type == "tuple":
        return _parse_complex
    if arg_type.startswith("uint") or arg_type.startswith("int"):
        return int
    if arg_type == "bool":
        return _parse_bool
    if arg_type == "address":
        return Web3.to_checksum_address
    if arg_type.startswith("bytes") or arg_type == "string":
        return _parse_string
    if arg_type.startswith("fixed") or arg_type.startswith("ufixed"):
        return float
    raise ValueError(f"cannot convert '{arg_type}' from string")


def _argument_parsers_for_params(
    outputs: Sequence[ABIComponent],
) -> List[ParamParser]:
    """
    Given the ABIFunctionParams object representing the output types
    of a specific function, return a list of string-to-paramtype
    converters.
    """

    out_types: List[ParamParser] = []
    for output in outputs:
        out_types.append(_string_to_argument_fn_for_type(output["type"]))

    return out_types


def _parse_return_value_from_type(
    type_name: str, output: ABIComponent, value: Any
) -> Any:
    """
    Parse a single value from an ABIFunctionParams.
    """

    # Check for array types
    if type_name.endswith("[]"):
        assert isinstance(value, list)
        element_type = type_name[:-2]
        return [
            _parse_return_value_from_type(element_type, output, v)
            for v in cast(List[Any], value)
        ]

    # Check for tuples
    if type_name == "tuple":
        assert isinstance(value, tuple)
        assert "components" in output
        return _parse_return_value_tuple(
            output["components"], cast(Tuple[Any, ...], value)
        )

    return value


def _parse_return_value_as_anonymous_tuple(
    outputs: Sequence[ABIComponent], values: Tuple[Any, ...]
) -> Tuple[Any, ...]:
    """
    Parse a list of unnamed ABIFunctionParams and a tuple, to a tuple.
    """
    assert len(values) == len(outputs)
    return tuple(
        _parse_return_value_from_type(out["type"], out, val)
        for val, out in zip(values, outputs)
    )


def _parse_return_value_as_named_tuple(
    outputs: Sequence[ABIComponent], values: Tuple[Any, ...]
) -> Dict[str, Any]:
    """
    Parse a list of named ABIFunctionParams and a tuple, to a dict.
    """

    assert len(values) == len(outputs)
    value_dict: Dict[str, Any] = {}
    for val, out in zip(values, outputs):
        if name := out.get("name"):
            value_dict[name] = _parse_return_value_from_type(out["type"], out, val)

    return value_dict


def _parse_return_value_tuple(
    outputs: Sequence[ABIComponent], values: Tuple[Any, ...]
) -> Any:
    """
    Anonymous tuples to tuples, named tuples to dictionaries.
    """

    assert len(values) == len(outputs)
    if outputs[0].get("name") == "":
        return _parse_return_value_as_anonymous_tuple(outputs, values)

    return _parse_return_value_as_named_tuple(outputs, values)
