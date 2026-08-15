# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: base.py
from pydantic import BaseModel


class Base(BaseModel):
    def __str__(self):
        fields_str = ", ".join(f"{k}={repr(v)}" for k, v in self.model_dump().items())
        return f"{self.__class__.__name__}({fields_str})"


__all__ = ["Base"]
