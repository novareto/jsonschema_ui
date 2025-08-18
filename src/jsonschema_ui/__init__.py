from typing import Mapping
from pydantic import BaseModel, Field


class Label(NamedTuple):
    value: str | int
    label: str


class UIField(BaseModel):
    title: str = Field(alias='ui:title')
    description: str = Field(alias='ui:description')
    attributes: dict = Field('ui:attributes', default_factory=dict)

    widget: str | None = Field('ui:widget', default=None)
    condition_logic: str | None = Field('ui:condition_logic', default=None)
    column: str | None = Field('ui:clumn', default=None)
    options: list[Label, ...] | None = Field('ui:options', default=None)



def parse_ui(ui_mapping: Mapping):
    uischema = {}
    for field, config in ui_mapping.items():
        uischema[field] = UIField(**config)
    import pdb
    pdb.set_trace()
