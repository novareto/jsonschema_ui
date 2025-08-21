import deform.widget
from jsonschema_colander.types import Object
from jsonschema_ui import parse_ui, apply_ui_to_colander


JSONSCHEMA = {
    "type": "object",
    "properties": {
        "geschlecht": {
            "title": "geschlecht",
            "description": "geschlecht",
            "type": "string",
            "enum": [
                "männlich",
                "weiblich"
            ]
        },
        "name": {
            "title": "Name",
            "description": "Name",
            "type": "string"
        },
        "land": {
            "title": "Land",
            "description": "in welchen Land leben Sie",
            "type": "string",
            "enum": [
                "Deutschland",
                "Schweiz",
                "sonstiges"
            ]
        },
        "land-sonstiges": {
            "title": "Land - sonstiges",
            "description": "Land - Sonstigaes",
            "type": "string"
        },
        "telefonnummern": {
            "type": "array",
            "title": "telefonnummern",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "geschlecht27bf5fa064c54c64bfe376079b29f5ff": {
                        "title": "geschlecht",
                        "type": "string",
                        "enum": [
                            "ja"
                        ]
                    },
                    "name3ed3690139e74a6ab90a8f767469d53e": {
                        "title": "name",
                        "type": "string"
                    }
                },
                "required": [],
            }
        }
    },
    "required": [
        "geschlecht",
        "telefonnummern"
    ],
}


UISCHEMA = {
    "geschlecht": {
        "ui:title": "geschlecht",
        "ui:description": "geschlecht",
        "ui:column": "col-md-12",
        "ui:attributes": {
            "data-condition-target": "name,land"
        },
        "ui:widget": "radio",
        "ui:options": [
            {
                "value": "männlich",
                "label": "männlich"
            },
            {
                "value": "weiblich",
                "label": "weiblich"
            }
        ]
    },
    "name": {
        "ui:title": "Name",
        "ui:description": "Name",
        "ui:column": "col-md-12",
        "ui:attributes": {
            "data-conditions": "{'field': 'geschlecht', 'operator': 'equals', 'value': 'männlich'}",
            "data-condition-logic": "and"
        }
    },
    "land": {
        "ui:title": "Land",
        "ui:description": "in welchen Land leben Sie",
        "ui:column": "col-md-12",
        "ui:attributes": {
            "data-conditions": "{'field': 'geschlecht', 'operator': 'equals', 'value': 'männlich'}",
            "data-condition-logic": "and",
            "data-condition-target": "land-sonstiges,land-sonstiges"
        },
        "ui:widget": "select",
        "ui:options": [
            {
                "value": "Deutschland",
                "label": "Deutschland"
            },
            {
                "value": "Schweiz",
                "label": "Schweiz"
            },
            {
                "value": "sonstiges",
                "label": "sonstiges"
            }
        ]
    },
    "land-sonstiges": {
        "ui:title": "Land - sonstiges",
        "ui:description": "Land - Sonstigaes",
        "ui:column": "col-md-12",
        "ui:attributes": {
            "data-conditions": "{'field': 'land', 'operator': 'equals', 'value': 'sonstiges'}",
            "data-condition-logic": "and"
        }
    },
    "telefonnummern.items.geschlecht27bf5fa064c54c64bfe376079b29f5ff": {
        "ui:title": "geschlecht",
        "ui:column": "col-md-12",
        "ui:attributes": {
            "data-condition-target": "name3ed3690139e74a6ab90a8f767469d53e"
        },
        "ui:widget": "radio",
        "ui:options": [
            {
                "value": "ja",
                "label": "ja"
            }
        ]
    },
    "telefonnummern.items.name3ed3690139e74a6ab90a8f767469d53e": {
        "ui:title": "name",
        "ui:column": "col-md-12",
        "ui:attributes": {
            "data-conditions": "{'field': 'geschlecht27bf5fa064c54c64bfe376079b29f5ff', 'operator': 'equals', 'value': 'ja'}",
            "data-condition-logic": "and"
        }
    },
    "telefonnummern": {
        "ui:title": "telefonnummern",
        "ui:column": "col-md-12",
        "ui:widget": "array"
    }
}


def test_complex_schema():
    schema = Object.from_json(JSONSCHEMA)()
    ui_schema = parse_ui(UISCHEMA)
    result = apply_ui_to_colander(
        schema,
        ui_schema,
        widgets={
            "select": deform.widget.SelectWidget,
            "radio": deform.widget.RadioChoiceWidget,
            "text": deform.widget.TextInputWidget,
            "array": deform.widget.SequenceWidget,
        }
    )
