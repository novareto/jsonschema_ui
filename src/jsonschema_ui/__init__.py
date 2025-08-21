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


def apply_ui_to_colander(
    schema: Schema, ui: Mapping[str, UIField], widgets: dict | None = None
):
    def find_field_by_path(node, path_parts):
        """Find field using path notation like 'telefonnummern.items.name'"""
        current = node
        
        for part in path_parts:
            found = False
            
            # Try direct access first
            if hasattr(current, '__getitem__') and part in current:
                current = current[part]
                found = True
            # Search in children
            elif hasattr(current, 'children'):
                for child in current.children:
                    if child.name == part:
                        current = child
                        found = True
                        break
            
            if not found:
                return None
                
        return current
    
    def find_field_recursive(node, field_name):
        """Fallback: recursively search for a field by name only"""
        if hasattr(node, '__getitem__') and field_name in node:
            return node[field_name]
        
        if hasattr(node, 'children'):
            for child in node.children:
                if child.name == field_name:
                    return child
                # Recursively search in nested schemas
                result = find_field_recursive(child, field_name)
                if result is not None:
                    return result
        return None
    
    for name, uifield in ui.items():
        field = None
        
        # If name contains dots, try path-based lookup first
        if '.' in name:
            path_parts = name.split('.')
            field = find_field_by_path(schema, path_parts)
        
        # If path-based lookup failed or no dots, try recursive search
        if field is None:
            field = find_field_recursive(schema, name)
        
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
