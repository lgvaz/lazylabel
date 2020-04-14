# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_core.ipynb (unless otherwise specified).

__all__ = ['AttrProxy', 'maintain_labels', 'Labeller', 'tasks_labels']

# Cell
from fastai2.basics import *

# Cell
_old_tfmdlists_init = TfmdLists.__init__
@patch
def __init__(self:TfmdLists, items, tfms, **kwargs):
    _old_tfmdlists_init(self, items, tfms, **kwargs)
    self.cached = False

# Cell
_old_tfmdlists_new = TfmdLists._new
@patch
def _new(self:TfmdLists, items, **kwargs):
    tls = _old_tfmdlists_new(self, items, )
    tls.cached = self.cached
    return tls

# Cell
@patch
def cache(self:TfmdLists, tfms=None, pbar=True):
    tfms = Pipeline(tfms)
    self.items = [tfms(o) for o in (progress_bar(self) if pbar else self)]
    self.cached = True

# Cell
_old_getitem = TfmdLists.__getitem__
@patch
def __getitem__(self:TfmdLists, idx):
    if self.cached: return super(TfmdLists, self).__getitem__(idx)
    else:      return _old_getitem(self, idx)

# Cell
class AttrProxy(GetAttr):
    def __init__(self, default): self.default = default

# Cell
def _get_proxy(x):
    if x.__class__.__module__ != 'builtins': raise ValueError('Use only with builtins')
    name = 'Proxy' + x.__class__.__name__.capitalize()
    return type(name, (x.__class__,), {})(x)

# Cell
def _add_attr(obj, name, value):
    try:
        setattr(obj, name, getattr(obj,'labels',value))
        return obj
    except AttributeError: return _add_attr(_get_proxy(obj), name, value)

# Cell
def _maintain_labels(old, new):
    if hasattr(old, 'labels'): new = _add_attr(new, 'labels', old.labels)
    return new

# Cell
def maintain_labels(f):
    def _inner(fn, x, **kwargs):
        return _maintain_labels(x, f(fn, x, **kwargs))
    return _inner

# Cell
# figure out delegates
_old_pipe_init = Pipeline.__init__
@patch
def __init__(self:Pipeline, *args, **kwargs):
    _old_pipe_init(self, *args, **kwargs)
    for o in self.fs: o._do_call = maintain_labels(o._do_call)

# Cell
# TODO: Can confirm function was called without doing "res is not x"?
@typedispatch
def subscribe(tfm:Transform):
    old_call = tfm._do_call
    tfm.broadcast = True
    def _inner(f):
        def _call(fn, x, **kwargs):
            res = old_call(fn, x, **kwargs)
            res = _maintain_labels(x, res)
            if tfm.broadcast:
                if res is not x: res = f(res)
            return res
        tfm._do_call = _call
        return f
    return _inner

# Cell
@patch
def broadcast(self:Pipeline, v):
    for f in self.fs: f.broadcast = v

# Cell
class Labeller:
    def __init__(self, abstain='abstain'): self.abstain = abstain

    def __call__(self, tfm):
        def _inner(f):
            return subscribe(tfm)(self._add_label(f))
        return _inner

    def _add_label(self, f):
        def _inner(x):
            label = ifnone(f(x), self.abstain)
            x = _add_attr(x, 'labels', [])
            x.labels.append(label)
            return x
        return _inner

# Cell
def tasks_labels(tls, vocab, splits=None, lazy=False):
    tasks = TfmdLists(tls, [AttrGetter('labels'), MultiCategorize(vocab)], splits=splits)
    if not lazy: tasks.cache()
    return tasks