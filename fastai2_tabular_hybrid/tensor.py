# AUTOGENERATED! DO NOT EDIT! File to edit: 01_Tensor.ipynb (unless otherwise specified).

__all__ = ['TensorDataset', 'TensorDataLoader', 'TensorDataLoaders']

# Cell
from fastai2.tabular.all import *

# Cell
class TensorDataset():
    "A `Tensor` dataset object from `TabularPandas`"
    def __init__(self, to:TabularPandas, device='cpu'):
        self.cats = tensor(to.cats.to_numpy()).to(device=device, dtype=torch.long)
        self.conts = tensor(to.conts.to_numpy()).to(device=device, dtype=torch.float32)
        self.ys = tensor(to.ys.to_numpy()).to(device)
        self.device = device

    def __getitem__(self, idx):
        idx = idx[0]
        return self.cats[idx:idx+self.bs], self.conts[idx:idx+self.bs], self.ys[idx:idx+self.bs]

    def __len__(self): return len(self.cats)

# Cell
class TensorDataLoader(DataLoader):
    def __init__(self, dataset, bs=1, **kwargs):
        "A `DataLoader` for a `TensorDataset`"
        super().__init__(dataset, bs=bs, **kwargs)
        self.dataset.bs = bs

    def create_item(self, s): return s

    def create_batch(self, b):
        cat, cont, y = self.dataset[b]
        return cat.to(self.device), cont.to(self.device), y.to(self.device)

# Cell
@patch
def shuffle_fn(x:TensorDataLoader):
    "Shuffle the interior dataset"
    rng = torch.randperm(len(x.dataset))
    x.dataset.cats = x.dataset.cats[rng]
    x.dataset.conts = x.dataset.conts[rng]
    x.dataset.ys = x.dataset.ys[rng]

# Cell
@patch
def get_idxs(x:TensorDataLoader):
    "Get index's to select"
    idxs = Inf.count if x.indexed else Inf.nones
    if x.n is not None: idxs = list(range(len(x.dataset)))
    if x.shuffle: x.shuffle_fn()
    return idxs

# Cell
class TensorDataLoaders(DataLoaders):
    """Transfers TabularPandas to TensorDataLoader for up to 20X speedup compared to TabularPandas DataLoader.

    Set device='cuda' for best performance. Will load entire dataset into GPU memory.

    Set dataset_device='cpu' if the dataset is too large for GPU memory.
    """

    def __init__(self, to:TabularPandas, bs=64, val_bs=None, shuffle_train=True,
                 device='cpu', dataset_device=None, **kwargs):
        dataset_device = device if dataset_device is None else dataset_device
        train_ds = TensorDataset(to.train, dataset_device)
        valid_ds = TensorDataset(to.valid, dataset_device)
        val_bs = bs*2 if val_bs is None else val_bs
        train = TensorDataLoader(train_ds, bs=bs, shuffle=shuffle_train, device=device, drop_last=True, **kwargs)
        valid = TensorDataLoader(valid_ds, bs=val_bs, shuffle=False, device=device, **kwargs)
        super().__init__(train, valid, device=device, **kwargs)