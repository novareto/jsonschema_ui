from typing import Mapping, NamedTuple
from pydantic import BaseModel, Field
from colander import Schema, deferred
from deform.widget import Widget
import deform.widget
import json
import logging

logger = logging.getLogger(__name__)


class Mask(NamedTuple):
    mask: str
    mask_placeholder: str


class Label(NamedTuple):
    value: str | int
    label: str


class UIField(BaseModel):
    title: str = Field(alias="ui:title")
    readonly: bool = Field(alias="ui:readonly", default=False)
    description: str = Field(alias="ui:description", default="")
    attributes: dict = Field(alias="ui:attributes", default_factory=dict)
    widget: str | None = Field(alias="ui:widget", default=None)
    css_class: str | None = Field(alias="ui:class", default=None)
    mask: Mask | None = Field(alias="ui:mask", default=None)
    options: list[Label] | None = Field(alias="ui:options", default=None)
    placeholder: str | None = Field(alias="ui:placeholder", default=None)
    conditions: list[dict] | None = Field(alias="ui:conditions", default=None)
    condition_logic: str | None = Field(alias="ui:condition_logic", default=None)
    unit: str | None = Field(alias="ui:unit", default=None)


def parse_ui(ui_mapping: Mapping):
    uischema = {}
    for field, config in ui_mapping.items():
        if "options" in config and "widget" not in config:
            raise KeyError("Options were provided but no widget.")
        uischema[field] = UIField(**config)
    return uischema


def find_field(node, path):
    # Handle bound schemas that might have a different structure
    if hasattr(node, "schema") and hasattr(node.schema, "children"):
        # This is a bound schema, use the underlying schema
        node = node.schema

    # For sequence/array nodes, "items" refers to the single child schema.
    # The colander Sequence has a single child that represents the item type.
    if path[0] == "items" and hasattr(node, "children") and len(node.children) == 1:
        node = node.children[0]
    elif hasattr(node, "__getitem__"):
        try:
            if path[0] in node:
                node = node[path[0]]
            else:
                raise KeyError(path[0])
        except (KeyError, TypeError):
            if hasattr(node, "children"):
                for child in node.children:
                    if child.name == path[0]:
                        node = child
                        break
                else:
                    logger.debug(f"Node {path[0]} not found in schema.")
                    return None
            else:
                logger.debug(f"Node {path[0]} not found in schema.")
                return None
    elif hasattr(node, "children"):
        for child in node.children:
            if child.name == path[0]:
                node = child
                break
        else:
            logger.debug(f"Node {path[0]} not found in schema.")
            return None
    else:
        logger.debug(f"Node {path[0]} not found in schema.")
        return None

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
        "checkbox": deform.widget.CheckboxChoiceWidget,
        "array": deform.widget.SequenceWidget,
        "date": deform.widget.DateInputWidget,
        "time": deform.widget.TimeInputWidget,
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
            # Attach UI conditions to the colander node so templates can render
            # data-conditions attributes for fields rendered by deform (e.g.
            # inside array items where the cpt_generator can't statically wrap
            # them with conditional-field markup).
            if uifield.unit:
                field._ui_unit = uifield.unit
            if uifield.conditions:
                field._ui_conditions_json = json.dumps(
                    {
                        "conditions": list(uifield.conditions),
                        "logic": uifield.condition_logic or "or",
                    }
                )
            if uifield.widget is not None:
                if uifield.widget not in widget_map:
                    raise ValueError(
                        f"Widget '{uifield.widget}' not found in widget mapping."
                    )
                widget = widget_map[uifield.widget]

                if isinstance(widget, deferred):
                    field.widget = widget
                    continue

                # For checkbox without options, use single CheckboxWidget
                if uifield.widget == "checkbox" and not uifield.options:
                    widget = deform.widget.CheckboxWidget
                options = {}
                if uifield.attributes:
                    options["attributes"] = uifield.attributes
                if uifield.readonly:
                    options["readonly"] = uifield.readonly
                if uifield.css_class:
                    if "attributes" not in options:
                        options["attributes"] = {}
                    options["attributes"]["class"] = uifield.css_class
                if uifield.options:
                    options["choices"] = uifield.options
                    options["values"] = uifield.options
                if uifield.mask:
                    options.update(uifield.mask._asdict())
                if uifield.placeholder:
                    if "attributes" not in options:
                        options["attributes"] = {}
                    options["attributes"]["placeholder"] = uifield.placeholder
                field.widget = widget(**options)
            else:
                if uifield.readonly:
                    field.widget.readonly = uifield.readonly
                if uifield.attributes and field.widget is not None:
                    field.widget.attributes = uifield.attributes
                if uifield.css_class and field.widget is not None:
                    if not hasattr(field.widget, "attributes"):
                        field.widget.attributes = {}
                    field.widget.attributes["class"] = uifield.css_class
                if uifield.options and field.widget is not None:
                    field.widget.choices = uifield.options
                if uifield.placeholder and field.widget is not None:
                    if not hasattr(field.widget, "attributes") or field.widget.attributes is None:
                        field.widget.attributes = {}
                    field.widget.attributes["placeholder"] = uifield.placeholder
        else:
            logger.debug(f"Feld '{name}' wurde im Schema nicht gefunden")
    return schema
