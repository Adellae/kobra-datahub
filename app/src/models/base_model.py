class BaseModel:
    def filter_by(self, df, sezona=None, soutez=None, tym=None):
        if sezona and sezona != "Vše":
            df = df[df["sezona"] == sezona]
        if soutez and soutez != "Vše":
            df = df[df["soutez"] == soutez]
        if tym and tym != "Vše":
            df = df[df["jednotny_nazev"] == tym]
        return df


    def get_metadata(self):
        """Vypíše základní metadata o datasetu"""
        if self.df is None:
            print("⚠️ DataFrame není načten.")
            return

        print("📊 Metadata o datovém modelu:")
        print(f"- Počet řádků: {self.df.shape[0]}")
        print(f"- Počet sloupců: {self.df.shape[1]}")
        print(f"- Sloupce:")
        for col in self.df.columns:
            print(f"  • {col} ({self.df[col].dtype})")