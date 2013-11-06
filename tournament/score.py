def calc_score(challenger, challenged, winner):
    if challenger == winner:
        return 2, 0
    elif challenged == winner:
        return -1, 1
    else:  # A tie!
        return 0, 0
