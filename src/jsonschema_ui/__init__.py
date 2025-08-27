from typing import Mapping, NamedTuple
from pydantic import BaseModel, Field
from colander import Schema
from deform.widget import Widget
import deform.widget


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
    css_class: str | None = Field(alias="ui:class", default=None)
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
    # Handle bound schemas that might have a different structure
    if hasattr(node, "schema") and hasattr(node.schema, "children"):
        # This is a bound schema, use the underlying schema
        node = node.schema

    if hasattr(node, "__getitem__") and path[0] in node:
        node = node[path[0]]
    elif hasattr(node, "children"):
        for child in node.children:
            if child.name == path[0]:
                node = child
                break
        else:
            raise LookupError(f"Node {path[0]} not found in schema.")
    else:
        raise LookupError(f"Node {path[0]} not found in schema.")

    if len(path) > 1:
        return find_field(node, path[1:])
    return node


def apply_ui_to_colander(
    schema: Schema, ui: Mapping[str, UIField], widgets: dict | None = None
):
    # Default widget mapping - can be overridden by widgets parameter
    default_widgets = {
        "radio": deform.widget.RadioChoiceWidget,
        "select": deform.widget.SelectWidget,
        "text": deform.widget.TextInputWidget,
        "textarea": deform.widget.TextAreaWidget,
        "password": deform.widget.PasswordWidget,
        "checkbox": deform.widget.CheckboxWidget,
        "array": deform.widget.SequenceWidget,
        "date": deform.widget.DateInputWidget,
        "datetime": deform.widget.DateTimeInputWidget,
        "datetime-local": deform.widget.DateTimeInputWidget,
        "hidden": deform.widget.HiddenWidget,
    }

    # Merge default widgets with user-provided widgets (user widgets take precedence)
    if widgets:
        widget_map = {**default_widgets, **widgets}
    else:
        widget_map = default_widgets

    for name, uifield in ui.items():
        path = name.split(".")
        field = find_field(schema, path)

        if field is not None:
            field.title = uifield.title
            field.description = uifield.description
            if uifield.widget is not None:
                if uifield.widget not in widget_map:
                    raise ValueError(
                        f"Widget '{uifield.widget}' not found in widget mapping."
                    )
                widget = widget_map[uifield.widget]
                options = {}
                if uifield.attributes:
                    options["attributes"] = uifield.attributes
                if uifield.css_class:
                    if "attributes" not in options:
                        options["attributes"] = {}
                    options["attributes"]["class"] = uifield.css_class
                if uifield.options:
                    options["choices"] = uifield.options
                    options["values"] = uifield.options
                if uifield.mask:
                    options.update(uifield.mask._asdict())
                field.widget = widget(**options)
            else:
                if uifield.attributes and field.widget is not None:
                    field.widget.attributes = uifield.attributes
                if uifield.css_class and field.widget is not None:
                    if not hasattr(field.widget, "attributes"):
                        field.widget.attributes = {}
                    field.widget.attributes["class"] = uifield.css_class
                if uifield.options and field.widget is not None:
                    field.widget.choices = uifield.options
        else:
            print(f"Warnung: Feld '{name}' wurde im Schema nicht gefunden")
    return schema
