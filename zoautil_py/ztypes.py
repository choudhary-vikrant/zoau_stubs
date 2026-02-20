from zoautil_py.common import clean_dataset_name as clean_dataset_name

class ZOAUResponse:
    rc: int
    stdout_response: str
    stderr_response: str
    command: str
    response_format: str
    def __init__(self, rc: str | int, stdout_response: str, stderr_response: str, command: str, response_format: str) -> None: ...
    def to_dict(self) -> dict[str, str | int]: ...
    @classmethod
    def from_dict(cls, response_as_dict) -> ZOAUResponse: ...

class DDStatement:
    name: str
    definition: str | DatasetDefinition | FileDefinition | list['DatasetDefinition']
    def __init__(self, name: str, definition: str | DatasetDefinition | FileDefinition | list['DatasetDefinition']) -> None: ...
    def get_mvscmd_string(self) -> str: ...

class DataDefinition:
    name: str
    def __init__(self, name: str) -> None: ...
    def build_arg_string(self) -> str: ...

class FileDefinition(DataDefinition):
    path_name: str
    normal_disposition: str | None
    abnormal_disposition: str | None
    path_mode: str | None
    status_group: str | None
    file_data: str | None
    record_length: str | None
    block_size: str | None
    record_format: str | None
    def __init__(self, path_name: str, normal_disposition: str | None = None, abnormal_disposition: str | None = None, path_mode: str | None = None, status_group: str | None = None, file_data: str | None = None, record_length: str | None = None, block_size: str | None = None, record_format: str | None = None) -> None: ...

class DatasetDefinition(DataDefinition):
    dataset_name: str
    disposition: str
    type: str | None
    primary: str | None
    primary_unit: str | None
    secondary: str | None
    secondary_unit: str | None
    normal_disposition: str | None
    abnormal_disposition: str | None
    conditional_disposition: str | None
    block_size: str | None
    record_format: str | None
    record_length: str | None
    storage_class: str | None
    data_class: str | None
    management_class: str | None
    key_length: str | None
    key_offset: str | None
    volumes: str | None
    dataset_key_label: str | None
    key_label1: str | None
    key_encoding1: str | None
    key_label2: str | None
    key_encoding2: str | None
    device_unit: str | None
    def __init__(self, dataset_name: str, disposition: str = 'SHR', type: str | None = None, primary: str | None = None, primary_unit: str | None = None, secondary: str | None = None, secondary_unit: str | None = None, normal_disposition: str | None = None, abnormal_disposition: str | None = None, conditional_disposition: str | None = None, block_size: str | None = None, record_format: str | None = None, record_length: str | None = None, storage_class: str | None = None, data_class: str | None = None, management_class: str | None = None, key_length: str | None = None, key_offset: str | None = None, volumes: str | None = None, dataset_key_label: str | None = None, key_label1: str | None = None, key_encoding1: str | None = None, key_label2: str | None = None, key_encoding2: str | None = None, device_unit: str | None = None) -> None: ...
