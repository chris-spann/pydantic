from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .utils import generate_table_heading, generate_table_row


@dataclass
class ExcludeSetting:
    name: str
    value: Union[bool, set]
    md_str: Optional[str] = None

    open_nowrap_span: str = '<span style="white-space: nowrap;">'
    close_nowrap_span: str = '</span>'

    @property
    def markdown_str(self) -> str:
        o = self.open_nowrap_span
        c = self.close_nowrap_span

        return self.md_str or f'{o}`{self.name}={self.value}`{c}'

    @property
    def kwargs_dict(self) -> Dict[str, Union[str, bool, set]]:
        return {} if self.name == 'not_specified' else {self.name: self.value}


field_exclude_settings: List[ExcludeSetting] = [
    ExcludeSetting(name='exclude', value=False),
    ExcludeSetting(name='exclude', value=True),
]
model_dump_exclude_overrides_settings: List[ExcludeSetting] = [
    ExcludeSetting(name='exclude', value={'name'}),
    ExcludeSetting(name='exclude', value={}),
    ExcludeSetting(name='include', value={'name'}),
    ExcludeSetting(name='include', value={}),
]
model_dump_exclude_variants_settings: List[ExcludeSetting] = [
    ExcludeSetting(name='not_specified', value={}, md_str='`<not specified>`'),  # special case
    ExcludeSetting(name='exclude_none', value=True),
    ExcludeSetting(name='exclude_defaults', value=True),
    ExcludeSetting(name='exclude_unset', value=True),
]


def build_exclude_priority_table(
    field_settings: List[ExcludeSetting],
    model_dump_settings: List[ExcludeSetting],
    constructor_kwargs: List[Dict[str, Any]],
) -> str:
    rows = []
    for kwargs_ in constructor_kwargs:
        for idx, model_dump_setting in enumerate(model_dump_settings):
            col_values = []
            for field_setting in field_settings:

                class Dog(BaseModel):
                    """Example class for explanation of `exclude` priority."""

                    name: Optional[str] = Field(default='Unspecified', **field_setting.kwargs_dict)

                my_dog = Dog(**kwargs_)
                result = my_dog.model_dump(**model_dump_setting.kwargs_dict)
                col_values.append(result)

            rows.append(
                generate_table_row(
                    col_values=[
                        f'`{kwargs_}`' if idx == 0 else '',
                        model_dump_setting.markdown_str,
                        *[f'`{x}`' for x in col_values],
                    ]
                )
            )

    table_heading = generate_table_heading(
        col_names=[
            '<br></br>`__init__` **kwargs**',
            '<br></br>`model_dump` **Setting**',
            f'`Field` **Setting**<br></br>{field_settings[0].markdown_str}',
            *[f'<br></br>{x.markdown_str}' for x in field_settings[1:]],
        ]
    )
    table = ''.join([table_heading, *rows])

    return table


exclude_overrides_table = build_exclude_priority_table(
    field_settings=field_exclude_settings,
    model_dump_settings=model_dump_exclude_overrides_settings,
    constructor_kwargs=[{'name': 'Ralph'}],
)
exclude_variants_table = build_exclude_priority_table(
    field_settings=field_exclude_settings,
    model_dump_settings=model_dump_exclude_variants_settings,
    constructor_kwargs=[{'name': 'Ralph'}, {'name': 'Unspecified'}, {'name': None}, {}],
)
