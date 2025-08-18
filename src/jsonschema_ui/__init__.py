from typing import Mapping, NamedTuple
from pydantic import BaseModel, Field
from colander import Schema
from deform.widget import Widget


class Label(NamedTuple):
    value: str | int
    label: str


class UIField(BaseModel):
    title: str = Field(alias='ui:title')
    description: str = Field(alias='ui:description')
    attributes: dict = Field(alias='ui:attributes', default_factory=dict)
    widget: str | None = Field(alias='ui:widget', default=None)
    column: str | None = Field(alias='ui:clumn', default=None)
    options: list[Label, ...] | None = Field(alias='ui:options', default=None)


def parse_ui(ui_mapping: Mapping):
    uischema = {}
    for field, config in ui_mapping.items():
        if 'options' in config and not 'widget' in config:
            raise KeyError('Options were provided but no widget.')
        uischema[field] = UIField(**config)
    return uischema


def apply_ui_to_colander(
        schema: Schema,
        ui: Mapping[str, UIField],
        widgets: dict | None = None
):
    for name, uifield in ui.items():
        if name in schema:
            field = schema[name]
            field.title = uifield.title
            field.description = uifield.description
            if uifield.widget is not None:
                widget = widgets[uifield.widget]
                options = {}
                if uifield.attributes:
                    options['attributes'] = uifield.attributes
                if uifield.options:
                    options['choices'] = uifield.options
                field.widget = widget(**options)
    return schema
