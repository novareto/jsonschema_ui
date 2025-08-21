import hamcrest
import colander
import deform.widget
from jsonschema_ui import parse_ui, UIField, apply_ui_to_colander


class Info(colander.Schema):
       age = colander.SchemaNode(
              colander.Integer(),
              description="Age"
       )
       date = colander.SchemaNode(
              colander.Date(),
              widget=deform.widget.DatePartsWidget(),
              description="Birth",
       )


class Person(colander.Schema):
       name = colander.SchemaNode(
              colander.String(), description="Content name"
       )
       info = Info()


class ComplexSchema(colander.Schema):
       id = colander.SchemaNode(colander.Integer())
       person = Person()


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
        widgets={"radio": deform.widget.RadioChoiceWidget}
    )


def test_nested_field_lookup():
       """Test that nested fields can be accessed via path notation"""
       ui = {
           "person.info.date": {
               "ui:title": "Birth Date",
               "ui:description": "Date of birth",
               "ui:widget": "date"
           }
       }
       ui_parsed = parse_ui(ui)
       schema = ComplexSchema()
       result = apply_ui_to_colander(schema, ui_parsed, widgets={"date": deform.widget.DateInputWidget})
       
       # Check that the nested field was found and modified
       date_field = schema['person']['info']['date']
       assert date_field.title == "Birth Date"
       assert date_field.description == "Date of birth"
