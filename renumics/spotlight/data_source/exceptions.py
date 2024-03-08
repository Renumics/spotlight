from fastapi import status

from renumics.spotlight.backend.exceptions import Problem


class InvalidDataSource(Problem):
    """The data source can't be opened"""

    def __init__(self) -> None:
        super().__init__(
            "Invalid data source",
            "Can't open supplied data source.",
            status.HTTP_403_FORBIDDEN,
        )
