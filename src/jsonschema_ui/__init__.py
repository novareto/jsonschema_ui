from typing import Mapping, NamedTuple
from pydantic import BaseModel, Field
from colander import Schema
from deform.widget import Widget


class Mask(NamedTuple):
    mask: str
    mask_placeholder: str


class Label(NamedTuple):
    value: str | int
    label: str


class UIField(BaseModel):
    title: str = Field(alias="ui:title")
    description: str = Field(alias="ui:description", default="")
    attributes: dict = Field(alias="ui:attributes", default_factory=dict)
    widget: str | None = Field(alias="ui:widget", default=None)
    column: str | None = Field(alias="ui:clumn", default=None)
    mask: Mask | None = Field(alias="ui:mask", default=None)
    options: list[Label, ...] | None = Field(alias="ui:options", default=None)


def parse_ui(ui_mapping: Mapping):
    uischema = {}
    for field, config in ui_mapping.items():
        if "options" in config and not "widget" in config:
            raise KeyError("Options were provided but no widget.")
        uischema[field] = UIField(**config)
    return uischema


def find_field(node, path):

    if hasattr(node, '__getitem__') and path[0] in node:
        node = node[path[0]]
    elif hasattr(node, 'children'):
        for child in node.children:
            if child.name == path[0]:
                node = child
                break
        else:
            raise LookupError('Node not found in schema.')
    else:
        raise LookupError('Node not found in schema.')

    if len(path) > 1:
        return find_field(node, path[1:])
    return node


def apply_ui_to_colander(
    schema: Schema, ui: Mapping[str, UIField], widgets: dict | None = None
):

    for name, uifield in ui.items():
        path = name.split('.')
        field = find_field(schema, path)

        if field is not None:
            field.title = uifield.title
            field.description = uifield.description
            if uifield.widget is not None:
                if not widgets:
                    raise ValueError(
                        f"Widgets mapping is missing while looking for {uifield.widget}."
                    )
                widget = widgets[uifield.widget]
                options = {}
                if uifield.attributes:
                    options["attributes"] = uifield.attributes
                if uifield.options:
                    options["choices"] = uifield.options
                    options["values"] = uifield.options
                if uifield.mask:
                    options.update(uifield.mask._asdict())
                field.widget = widget(**options)
            else:
                if uifield.attributes and field.widget is not None:
                    field.widget.attributes = uifield.attributes
                if uifield.options and field.widget is not None:
                    field.widget.choices = uifield.options
        else:
            print(f"Warnung: Feld '{name}' wurde im Schema nicht gefunden")
    return schema
