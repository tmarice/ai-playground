"""DataSource class for wrapping CSV files and exposing metadata."""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ColumnMetadata:
    """Metadata for a single column in a dataset."""

    name: str
    description: str = ""
    dtype: str = "unknown"
    unique_count: int = 0
    null_count: int = 0
    sample_values: list[str] = field(default_factory=list)

    def to_description_line(self) -> str:
        """Generate a description line for this column."""
        parts = [f"  - {self.name}"]
        if self.dtype != "unknown":
            parts.append(f"({self.dtype})")
        parts.append(f": {self.description or '[Add description]'}")
        return " ".join(parts)


@dataclass
class DataSourceMetadata:
    """Aggregated metadata for a data source."""

    row_count: int = 0
    columns: list[ColumnMetadata] = field(default_factory=list)
    file_size_bytes: int = 0
    encoding: str = "utf-8"

    @property
    def column_names(self) -> list[str]:
        """Get list of column names."""
        return [col.name for col in self.columns]

    def get_column(self, name: str) -> ColumnMetadata | None:
        """Get column metadata by name."""
        for col in self.columns:
            if col.name == name:
                return col
        return None


class DataSource:
    """Wrapper for CSV files that exposes metadata and data access."""

    def __init__(self, filepath: Path) -> None:
        """Initialize a DataSource from a CSV file.

        Args:
            filepath: Path to the CSV file

        Raises:
            ValueError: If the file is not a valid CSV
            FileNotFoundError: If the file does not exist
        """
        self._filepath = filepath
        self._metadata: DataSourceMetadata | None = None
        self._description: str = ""
        self._validate_and_load()

    def _validate_and_load(self) -> None:
        """Validate the CSV file and load metadata."""
        if not self._filepath.exists():
            raise FileNotFoundError(f"File does not exist: {self._filepath}")

        if not self._filepath.is_file():
            raise ValueError(f"Not a file: {self._filepath}")

        if self._filepath.suffix.lower() != ".csv":
            raise ValueError(f"Not a CSV file: {self._filepath}")

        self._load_metadata()

    def _infer_dtype(self, values: list[str]) -> str:
        """Infer the data type from a list of string values."""
        non_empty = [v for v in values if v.strip()]
        if not non_empty:
            return "empty"

        int_count = 0
        float_count = 0
        bool_count = 0
        date_count = 0

        for val in non_empty:
            val = val.strip()

            # Check for boolean strings (excluding pure numeric 1/0)
            if val.lower() in ("true", "false", "yes", "no"):
                bool_count += 1
                continue

            # Check for integers first
            try:
                int(val)
                int_count += 1
                continue
            except ValueError:
                pass

            # Check for floats
            try:
                float(val)
                float_count += 1
                continue
            except ValueError:
                pass

            # Check for dates
            if self._looks_like_date(val):
                date_count += 1

        total = len(non_empty)
        if int_count == total:
            return "integer"
        if int_count + float_count == total:
            return "numeric"
        if bool_count == total:
            return "boolean"
        if date_count > total * 0.8:
            return "date"
        return "text"

    def _looks_like_date(self, val: str) -> bool:
        """Check if a value looks like a date."""
        import re

        date_patterns = [
            r"^\d{4}-\d{2}-\d{2}$",
            r"^\d{2}/\d{2}/\d{4}$",
            r"^\d{2}-\d{2}-\d{4}$",
            r"^\d{4}/\d{2}/\d{2}$",
        ]
        return any(re.match(p, val) for p in date_patterns)

    def _load_metadata(self) -> None:
        """Load metadata from the CSV file."""
        file_size = self._filepath.stat().st_size

        try:
            with self._filepath.open("r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)

                if header is None:
                    raise ValueError(f"CSV file is empty: {self._filepath}")

                if not header or all(col.strip() == "" for col in header):
                    raise ValueError(f"CSV file has empty header: {self._filepath}")

                rows: list[list[str]] = []
                for row in reader:
                    rows.append(row)

                columns: list[ColumnMetadata] = []
                for i, col_name in enumerate(header):
                    col_values = [row[i] if i < len(row) else "" for row in rows]

                    unique_values = set(col_values)
                    null_count = sum(1 for v in col_values if not v.strip())
                    sample_values = list(unique_values - {""})[:5]
                    dtype = self._infer_dtype(col_values)

                    columns.append(
                        ColumnMetadata(
                            name=col_name.strip(),
                            dtype=dtype,
                            unique_count=len(unique_values),
                            null_count=null_count,
                            sample_values=sample_values,
                        )
                    )

                self._metadata = DataSourceMetadata(
                    row_count=len(rows),
                    columns=columns,
                    file_size_bytes=file_size,
                    encoding="utf-8",
                )

        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {e}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Unable to read as UTF-8: {e}")

    @property
    def filepath(self) -> Path:
        """Get the file path."""
        return self._filepath

    @property
    def name(self) -> str:
        """Get the file name."""
        return self._filepath.name

    @property
    def metadata(self) -> DataSourceMetadata:
        """Get the metadata for this data source."""
        if self._metadata is None:
            self._load_metadata()
        return self._metadata  # type: ignore

    @property
    def description(self) -> str:
        """Get the user-provided description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Set the user-provided description."""
        self._description = value

    @property
    def columns(self) -> list[ColumnMetadata]:
        """Get the list of columns."""
        return self.metadata.columns

    @property
    def column_names(self) -> list[str]:
        """Get the list of column names."""
        return self.metadata.column_names

    @property
    def row_count(self) -> int:
        """Get the number of data rows (excluding header)."""
        return self.metadata.row_count

    def get_column_description(self, column_name: str) -> str:
        """Get the description for a specific column."""
        col = self.metadata.get_column(column_name)
        return col.description if col else ""

    def set_column_description(self, column_name: str, description: str) -> None:
        """Set the description for a specific column."""
        col = self.metadata.get_column(column_name)
        if col:
            col.description = description

    def generate_description_template(self) -> str:
        """Generate a description template with column information."""
        lines = [
            f"Dataset: {self.name}",
            f"Rows: {self.row_count}",
            f"Size: {self._format_size(self.metadata.file_size_bytes)}",
            "",
            "Columns:",
        ]

        for col in self.columns:
            line = f"  - {col.name} ({col.dtype})"
            if col.sample_values:
                samples = ", ".join(col.sample_values[:3])
                line += f" [e.g., {samples}]"
            line += f": {col.description or '[Add description]'}"
            lines.append(line)

        return "\n".join(lines)

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable form."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def read_rows(
        self, limit: int | None = None, offset: int = 0
    ) -> list[dict[str, str]]:
        """Read rows from the CSV file as dictionaries.

        Args:
            limit: Maximum number of rows to return (None for all)
            offset: Number of rows to skip

        Returns:
            List of row dictionaries
        """
        rows: list[dict[str, str]] = []
        try:
            with self._filepath.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i < offset:
                        continue
                    if limit is not None and len(rows) >= limit:
                        break
                    rows.append(dict(row))
        except (csv.Error, UnicodeDecodeError):
            pass
        return rows

    def get_summary(self) -> dict[str, Any]:
        """Get a summary dictionary of the data source."""
        return {
            "name": self.name,
            "path": str(self._filepath),
            "row_count": self.row_count,
            "column_count": len(self.columns),
            "columns": [
                {
                    "name": col.name,
                    "dtype": col.dtype,
                    "unique_count": col.unique_count,
                    "null_count": col.null_count,
                    "description": col.description,
                }
                for col in self.columns
            ],
            "file_size_bytes": self.metadata.file_size_bytes,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return f"DataSource({self.name!r}, columns={self.column_names})"


def load_datasources(filepaths: list[Path]) -> list[DataSource]:
    """Load multiple data sources from file paths.

    Args:
        filepaths: List of CSV file paths

    Returns:
        List of successfully loaded DataSource objects
    """
    datasources: list[DataSource] = []
    for path in filepaths:
        try:
            datasources.append(DataSource(path))
        except (ValueError, FileNotFoundError) as e:
            print(f"Warning: Could not load {path}: {e}")
    return datasources
