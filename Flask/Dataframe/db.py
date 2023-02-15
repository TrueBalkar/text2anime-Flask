from Model import model


class DB:
    print("[SETTINGS THINGS UP...]")
    print("[INITIALIZING DATAFRAMES...]")
    df, desc, char_desc, reviews, shiet = model.initialise_df()
    print("[DATAFRAMES INITIALIZED]")
    print("[CALCULATING MEAN...]")
    char_desc_general, reviews_general, desc_general = model.get_general(char_desc, reviews, desc)
    print("[MEAN CALCULATED]")
    print("[INITIALIZING LASER...]")
    laser = model.initialise_laser()
    print("[LASER INITIALIZED]")
    stop = model.get_stop_words()

    def get_df(self):
        return self.df, self.desc, self.char_desc, self.reviews, self.shiet, self.char_desc_general, \
            self.reviews_general, self.desc_general, self.laser, self.stop
