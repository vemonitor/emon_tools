"""
Common Pydantic Models for Fina Files processing.
"""
from enum import Enum
from typing import ClassVar
from typing import Optional
from typing import Union
from typing_extensions import Annotated
from pydantic import BaseModel, model_validator
from pydantic import Field
from pydantic import ConfigDict
from pydantic import StrictFloat
from pydantic import StrictInt
from pydantic import StrictStr


class OutputType(str, Enum):
    """Output Selected for FinaData methods"""
    # [mean] or [value]
    VALUES = "values"
    # [min, mean, max]
    VALUES_MIN_MAX = "valuesMinMax"
    # [time, mean] or [time, value]
    TIME_SERIES = "timeSeries"
    # [time, min, mean, max]
    TIME_SERIES_MIN_MAX = "timeSeriesMinMax"
    # [time, finite_count, total_count]
    INTEGRITY = "integrity"


class OutputAverageEnum(str, Enum):
    """
    Enumeration for define how averaged values are computed.
    This enumeration defines how averaged values are computed.

    Attributes:
        COMPLETE (str):
    """
    # accept only complete chunks of data
    COMPLETE = "complete"
    # accept partial chunks of data
    PARTIAL = "partial"

    AS_IS = "as_is"


class TimeRefEnum(str, Enum):
    """
    Enumeration for Time Reference in Averaged Values.

    This enumeration defines the time reference options
    for averaging values over a fixed interval.

    Attributes:
        BY_TIME (str):
            Fixes the time reference to the current start time
            based on the fixed interval.
            Example: For a 20-second interval,
            averaged values times can be 00:00:00, 00:00:20, 00:00:40.
        BY_SEARCH (str):
            Fixes the time reference from the current search start time.
            Example: For a 20-second interval and a start time of 00:00:08,
            averaged values times can be 00:00:08, 00:00:28, 00:00:48.
    """
    # stats time ref is fixed to time_start % interval
    BY_TIME = "by_time"
    BY_SEARCH = "by_search"


class FinaReaderParamsModel(BaseModel):
    """Fina Reader Params Model Validation"""
    data_dir: Annotated[
        StrictStr,
        Field(
            min_length=1,
            max_length=255,
            pattern=r"^[A-Za-z0-9-_/\\.:]+$",
            title="Fina File Name"
        )
    ]
    file_name: Annotated[
        StrictStr,
        Field(
            min_length=1,
            max_length=60,
            pattern=r"^[A-Za-z0-9-_]+$",
            title="Fina File Name"
        )
    ]


class FinaBaseParamsModel(BaseModel):
    """Fina Shared Params Model Validation"""
    model_config = ConfigDict(from_attributes=True)

    time_interval: Annotated[
        StrictInt,
        Field(ge=0, title="Time Interval", default=0)
    ]
    min_value: Annotated[
        Optional[Union[StrictInt, StrictFloat]],
        Field(title="Min Value", default=None)
    ]
    max_value: Annotated[
        Optional[Union[StrictInt, StrictFloat]],
        Field(title="Max Value", default=None)
    ]
    n_decimals: Annotated[
        StrictInt,
        Field(
            ge=0,
            title="Number of Decimals",
            default=3
        )
    ]
    output_type: Annotated[
        OutputType,
        Field(
            title="Output Type",
            default=OutputType.TIME_SERIES)
    ]
    output_average: Annotated[
        OutputAverageEnum,
        Field(
            title="Average Output",
            description="Define how averaged values are computed",
            default=OutputAverageEnum.COMPLETE)
    ]
    time_ref_start: Annotated[
        TimeRefEnum,
        Field(
            title="Time Ref",
            description="Time Ref for averaged values",
            default=TimeRefEnum.BY_TIME)
    ]


class FinaByTimeParamsModel(FinaBaseParamsModel):
    """Get PhpFina data endpoint args"""
    start_time: Annotated[
        StrictInt,
        Field(ge=0, title="Start Time", default=0)
    ]
    time_window: Annotated[
        StrictInt,
        Field(ge=0, title="Time Window", default=0)
    ]


class FinaByDateParamsModel(FinaBaseParamsModel):
    """Get PhpFina data endpoint args"""
    start_date: Annotated[
        StrictStr,
        Field(max_length=50, title="Start Date")
    ]
    time_window: Annotated[
        StrictInt,
        Field(ge=0, title="Time Window", default=0)
    ]
    date_format: Annotated[
        StrictStr,
        Field(
            max_length=50,
            title="Date Format",
            default="%Y-%m-%d %H:%M:%S"
        )
    ]


class FinaByDateRangeParamsModel(FinaBaseParamsModel):
    """Get PhpFina data endpoint args"""
    start_date: Annotated[
        StrictStr,
        Field(max_length=50, title="Start Date")
    ]
    end_date: Annotated[
        StrictStr,
        Field(max_length=50, title="End Date")
    ]
    date_format: Annotated[
        StrictStr,
        Field(
            max_length=50,
            title="Date Format",
            default="%Y-%m-%d %H:%M:%S"
        )
    ]


class FinaMetaModel(BaseModel):
    """Get PhpFina data endpoint args"""
    interval: Annotated[StrictInt, Field(ge=0, title="Interval")]
    start_time: Annotated[StrictInt, Field(ge=0, title="Start Time")]
    end_time: Annotated[StrictInt, Field(ge=0, title="End Time")]
    npoints: Annotated[StrictInt, Field(ge=0, title="Number of Points")]
    size: Annotated[StrictInt, Field(ge=0, title="File Size")]

    @model_validator(mode='after')
    def _validate_date_order(self):
        """
        Ensure that start_time precedes end_time.

        Raises:
            ValueError: If start_time is not less than end_time.
        """
        if self.start_time > 0 and self.start_time >= self.end_time:
            raise ValueError("start_time must be less than end_time.")
        return self


class FileReaderPropsModel(BaseModel):
    """Output Mean Selected for FinaData methods"""
    # Prefered number of values to read in a chunk
    # 4 B = 4096 bytes / 4 bytes = 1024 points
    DEFAULT_CHUNK_SIZE: ClassVar[int] = 1024
    # Max number of values to read in a chunk
    # 64 KB = 16384 bytes / 4 bytes = 4096 points
    CHUNK_SIZE_LIMIT: ClassVar[int] = 4096

    meta: Annotated[
        FinaMetaModel,
        Field(
            title="File Meta", description="File Meta data"
        )
    ]
    search: Annotated[
        FinaByTimeParamsModel,
        Field(
            title="File Meta", description="File Meta data"
        )
    ]
    current_pos: Annotated[
        StrictInt,
        Field(
            ge=0, title="Current Pos",
            description="Reading Current Position",
            default=0
        )
    ]
    start_pos: Annotated[
        StrictInt,
        Field(
            ge=0, title="Start Pos",
            description="Reading Start Position",
            default=0
        )
    ]
    chunk_size: Annotated[
        StrictInt,
        Field(
            ge=0,
            title="Chunk Size",
            description="Chunk Size to Read",
            default=0
        )
    ]
    remaining_points: Annotated[
        StrictInt,
        Field(
            ge=0,
            title="Remaining points",
            description="Remaining points to read",
            default=0
        )
    ]
    start_search: Annotated[
        StrictInt,
        Field(
            ge=0, title="Start Search",
            description="Search Start points to retrieve",
            default=0
        )
    ]
    window_search: Annotated[
        StrictInt,
        Field(
            ge=0, title="Window Search",
            description="Window of points to retrieve",
            default=0
        )
    ]
    block_size: Annotated[
        StrictInt,
        Field(
            ge=0, title="Block Size",
            description="interval block size for averaging values",
            default=0
        )
    ]
    current_window: Annotated[
        StrictInt,
        Field(
            ge=0, title="Current Window",
            description="Current window in interval block size",
            default=0
        )
    ]
    window_max: Annotated[
        StrictInt,
        Field(
            ge=0, title="Current Window Max",
            description="Current window Max value",
            default=0
        )
    ]
    current_start: Annotated[
        StrictInt,
        Field(
            ge=0, title="Current Start Point",
            description="Current Start Point to read in file",
            default=0
        )
    ]
    next_start: Annotated[
        StrictInt,
        Field(
            ge=0, title="Next Start Point",
            description="Next Start Point to read in file",
            default=0
        )
    ]
    auto_pos: Annotated[
        bool,
        Field(
            title="Auto Pos",
            description="Is position calculated on each loop",
            default=True
        )
    ]
