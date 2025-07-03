from src.models.base_model import BaseModel
from src.data.loader import load_fakt_brankari, load_dim_tym, load_dim_zapasy, load_dim_datum, load_dim_hrac

class BrankariModel(BaseModel):
    def __init__(self):
        self.df = (
            load_fakt_brankari()
            .merge(load_dim_tym(), on="id_tym", how="left", suffixes=('', '_drop'))
            .merge(load_dim_datum(), on="id_datum", how="left", suffixes=('', '_drop'))
            .merge(load_dim_zapasy(), on="id_zapas", how="left", suffixes=('', '_drop'))
            .merge(load_dim_hrac(), on="id_hrac", how="left", suffixes=('', '_drop'))
        )

    def get_filtered(self, sezona=None, soutez=None, tym=None):
        return self.filter_by(self.df, sezona, soutez, tym)
