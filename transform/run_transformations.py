from config import DB_PATHS
from transform.mapping.map_nazev_tym
from transform.mapping.map_zkratka_tym

from transform.dimensions.dw_dim_cas import transform_dw_dim_cas
from transform.dimensions.dw_dim_datum import transform_dw_dim_datum
from transform.dimensions.dw_dim_hrac import transform_dw_dim_hrac
from transform.dimensions.dw_dim_tym import transform_dw_dim_tym
from transform.dimensions.dw_dim_zapas import transform_dw_dim_zapas

from transform.facts.dw_fakt_akce import transform_fakt_akce
from transform.facts.dw_fakt_akce import transform_dw_fakt_tresty



def main():
    with sqlite3.connect(DB_PATHS["DW"]) as conn:

        # Mapping tables
        transform_map_nazev_tym(conn)
        transform_map_zkratka_tym(conn)

        # Dimensions
        transform_dw_dim_datum(conn)
        transform_dw_dim_cas(con)
        transform_dw_dim_hrac(conn)
        transform_dw_dim_tym(conn)
        transform_dw_dim_zapas(conn)

        # Facts
        transform_fakt_akce(conn)
        transform_dw_fakt_tresty(conn)
        transform_dw_fakt_hraci(conn)
        transform_dw_fakt_brankari(conn)
        

    conn.close()




if __name__ == "__main__":
    main()
