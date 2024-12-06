"""
Constants
"""

COMMISSION_RATE_PRECISION = 10000


class AutonDenoms:
    """
    Auton sub-denominations. 1 auton = one quntillion wei and
    common auton sub-denominations are expressed as base10 power
    multiples of wei. These conventions are borrowed from and
    consistent with Ethereum's ether denomination conventions
    See: https://github.com/web3/web3.js/blob/0.15.0/lib/utils/utils.js#L40
    """

    KWEI_VALUE_IN_WEI = 1000  # 10^3  (femtoton)
    MWEI_VALUE_IN_WEI = 1000000  # 10^6  (picoton)
    GWEI_VALUE_IN_WEI = 1000000000  # 10^9  (nanoton)
    SZABO_VALUE_IN_WEI = 1000000000000  # 10^12 (microton)
    FINNEY_VALUE_IN_WEI = 1000000000000000  # 10^15 (milliton)
    AUTON_VALUE_IN_WEI = 1000000000000000000  # 10^18 (ton)


class UnixExitStatus:
    """Unix exit status codes to return on exception throws.

    To make aut friendly to systems people who might use the command
    in their shell scripts, aut exceptions will also return meaningful
    exit codes to the shell. Each of these constants define an exit
    code that corresponds to a certain type of error. Unix commands
    return exit codes. 0 means 'success' and non-zero means failure of
    some sort. 1 is conventionally a catch-all error code, 2 is for
    misuse of built-in shell commands, and there are also some other
    ranges that have special meanings. Exit codes 0 and 64-113 can be
    safely assumed to be usable by applications without clashing with
    these special meanings, so we'll use that range:
    - 64-99, autonity error range
    - 100-113, generic Web3 error range
    Sources:
    - https://tldp.org/LDP/abs/html/exitcodes.html
    - https://docs.python.org/3/library/sys.html#sys.exit
    - https://eips.ethereum.org/EIPS/eip-1474
    """

    CLI_INVALID_INVOCATION = 64
    CLI_INVALID_OPTION_VALUE = 65
    WEB3_PARSE_ERROR = 100  # -32700 "Invalid JSON"
    WEB3_INVALID_REQUEST = 101  # -32600 "JSON is not a valid request"
    WEB3_METHOD_NOT_FOUND = 102  # -32601 "Method does not exist"
    WEB3_INVALID_PARAMS = 103  # -32602 "Invalid method parameters"
    WEB3_INTERNAL_ERROR = 104  # -32603 "Internal JSON-RPC error"
    WEB3_INVALID_INPUT = 105  # -32000 "Missing or invalid parameters"
    WEB3_RESOURCE_NOT_FOUND = 106  # -32001 "Requested resource not found"
    WEB3_RESOURCE_UNAVAILABLE = 107  # -32002 "Requested resource not available"
    WEB3_TRANSACTION_REJECTED = 108  # -32003 "Transaction creation failed"
    WEB3_METHOD_NOT_SUPPORTED = 109  # -32004 "Method is not implemented"
    WEB3_LIMIT_EXCEEDED = 110  # -32005 "Request exceeds defined limit"
    WEB3_JSON_RPC_VERSION_NOT_SUPPORTED = (
        111  # -32006 "Version of JSON-RPC protocol not supported"
    )
