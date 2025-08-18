import hamcrest
import colander
from deform.widget import RadioChoiceWidget
from jsonschema_ui import parse_ui, UIField, apply_ui_to_colander


class DocumentSchema(colander.Schema):

       title = colander.SchemaNode(
           colander.String(),
           title='Title',
           validator=colander.Length(min=5, max=100)
       )

       type = colander.SchemaNode(
           colander.String(),
           title='Type'
       )

       body = colander.SchemaNode(
           colander.String(),
           title='Body',
           description='Body'
       )


EXAMPLE = {
    "title": {
        "ui:title": "Title of the document",
        "ui:description": "Representative title of the document",
        "ui:column": "col-md-12",
    },
    "type": {
        "ui:title": "Type of document",
        "ui:description": "Representative title of the document",
        "ui:column": "col-md-12",
        "ui:widget": "radio",
        "ui:options": [
            {
                "value": "insurance",
                "label": "Car innsurance"
            },
            {
                "value": "contract",
                "label": "Security contract"
            }
        ],
        "ui:attributes": {
            "data-condition-target": "body"
        }
    },
    "body": {
        "ui:title": "Body",
        "ui:description": "Core text containing a full contract",
        "ui:column": "col-md-12",
        "ui:attributes": {
            "data-condition-logic": "and",
            "data-conditions": '''{"field": "type", "operator": "equals", "value": "contract"}'''
        }
    }
}


def test_schema():
    result = parse_ui(EXAMPLE)



def test_apply():
    ui = parse_ui(EXAMPLE)
    result = apply_ui_to_colander(
        DocumentSchema(),
        ui,
        widgets={"radio": RadioChoiceWidget}
    )
