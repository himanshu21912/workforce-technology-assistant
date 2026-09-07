from collections.abc import Sequence
from typing import TypeVar


MessageType = TypeVar("MessageType")


def apply_message_window(
    messages: Sequence[MessageType],
    maximum_messages: int,
) -> list[MessageType]:
    if maximum_messages < 1:
        raise ValueError(
            "maximum_messages must be greater than zero."
        )

    if len(messages) <= maximum_messages:
        return list(messages)

    return list(messages[-maximum_messages:])