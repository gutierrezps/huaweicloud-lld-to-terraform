from io import TextIOWrapper
from pystache import Renderer

from .utils import clean_str


class Resource2Terraform:
    def __init__(self, template_name: str, key_attr: str) -> None:
        self._template_name = template_name

        self._attr_clean = {}
        self._resources_data = {}
        self._last_id = 0
        self._key_attr = key_attr

    def add(self, resource_data: dict):
        resource_data = self._clean(resource_data)

        resource_data = self._parse(resource_data)

        error_msg = self._validate(resource_data)
        if error_msg is not None:
            return error_msg

        self._resources_data[resource_data[self._key_attr]] = resource_data

    def to_dict(self) -> dict:
        return self._resources_data

    def to_terraform(self, output_file: TextIOWrapper):
        """Transforms all resource data into Terraform code, and write to
        output_file.

        Args:
            output_file (TextIOWrapper): file to write the tf code
        """
        renderer = Renderer()
        template_filename = f'templates/{ self._template_name }'
        variation = ''

        for resource_data in self._resources_data.values():
            if 'template_variation' in resource_data:
                variation = '-' + resource_data['template_variation']

            tf_code = renderer.render_name(
                template_filename + variation, resource_data)
            tf_code += '\n'
            output_file.write(tf_code)

    def _clean(self, resource_data: dict):
        for new_key, orig_key in self._attr_clean.items():
            if orig_key not in resource_data:
                continue
            resource_data[new_key] = clean_str(resource_data[orig_key])

        return resource_data

    def _parse(self, resource_data: dict):
        return resource_data

    def _validate(self, resource_data: dict, error_msg: str | None = None):
        if error_msg is not None:
            return error_msg

        if resource_data[self._key_attr] in self._resources_data:
            error_msg = f'duplicate { self._key_attr } name '
            error_msg += f'({resource_data[self._key_attr]})'

        return error_msg
