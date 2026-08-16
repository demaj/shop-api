from typing import Any, ClassVar

from pydantic import BaseModel


class PartialUpdate(BaseModel):
    """Partial-update body: an explicit null means "unchanged" except for NULLABLE_FIELDS."""

    NULLABLE_FIELDS: ClassVar[frozenset[str]] = frozenset()

    def changes(self) -> dict[str, Any]:
        data = self.model_dump(exclude_unset=True)
        return {key: value for key, value in data.items() if value is not None or key in self.NULLABLE_FIELDS}
