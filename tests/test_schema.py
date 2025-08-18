import hamcrest
from jsonschema_ui import parse_ui, UIField


EXAMPLE = {
  "geschlecht": {
    "ui:title": "geschlecht",
    "ui:description": "geschlecht",
    "ui:column": "col-md-12",
    "ui:attributes": {
      "data-condition-target": "name"
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
    "ui:conditions": [
      {
        "field": "geschlecht",
        "operator": "equals",
        "value": "männlich"
      }
    ],
    "ui:condition_logic": "and"
  }
}


def test_schema():
    result = parse_ui(EXAMPLE)
