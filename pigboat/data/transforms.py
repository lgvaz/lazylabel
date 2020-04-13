# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_data.transforms.ipynb (unless otherwise specified).

__all__ = ['CategorizeTaskLabels']

# Cell
from fastai2.basics import *

# Cell
class CategorizeTaskLabels(MultiCategorize):
    def encodes(self, o): o.labels = super().encodes(o.labels); return o
    def decodes(self, o): o.labels = super().decodes(o.labels); return o