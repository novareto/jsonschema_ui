import hamcrest
import colander
import deform.widget
from jsonschema_ui import parse_ui, UIField, apply_ui_to_colander, find_field


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
       schema = ComplexSchema()
       result = find_field(schema, ["person", "info", "date"])
       assert result is schema["person"]["info"]["date"]

       result = find_field(schema, ["id"])
       assert result is schema["id"]


def test_apply_nest_ui():
       ui_parsed = parse_ui({
              "id": {
                     "ui:title": "Person unique id",
                     "ui:description": "Unique int id for a person.",
              },
              "person.info.date": {
                     "ui:title": "Birth Date",
                     "ui:description": "Date of birth",
                     "ui:widget": "date"
              }
       })
       schema = ComplexSchema()
       result = apply_ui_to_colander(
              schema,
              ui_parsed,
              widgets={"date": deform.widget.DateInputWidget}
       )

       date_field = schema["person"]["info"]["date"]
       assert date_field.title == "Birth Date"
       assert date_field.description == "Date of birth"
       assert isinstance(date_field.widget, deform.widget.DateInputWidget)

       id_field = schema["id"]
       assert id_field.title == "Person unique id"
       assert id_field.description == "Unique int id for a person."
