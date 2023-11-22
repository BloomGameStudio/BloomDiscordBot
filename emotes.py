##If a contributors emoji is detected in chat, react and ping that user every 4 hrs

#ToDO:
##Only ping during waking hours
##Documentation

##Static assignment for initial run
##Functions exist to add, or remove contributors.
class Contributor:
    def __init__(self, name, uid, utc_start_time, utc_end_time):
        self.name = name
        self.uid = uid
        self.actioned = False
        self.utc_start_time = utc_start_time
        self.utc_end_time = utc_end_time

contributors = [
    Contributor("Sarahtonein", "316765092689608706", 1, 5),
    Contributor("Lapras", "395761182939807744", 1, 5),
    Contributor("Balu", "353572599957291010", 1, 5),
    Contributor("Pizzacat", "303732860265693185", 1, 5),
    Contributor("Spaghetto", "406302927884386318", 1, 5),
    Contributor("Lilgumbo", "368617749041381388", 1, 5),
    Contributor("Baguette", "548974112131776522", 1, 5),
    Contributor("Bagelface", "856041684588167188", 1, 5),
    Contributor("Breeze", "154033306894073856", 1, 5),
    Contributor("Ploxx95", "406073034160472066", 1, 5)
]

emoji_id_mapping = {
    "<:sarah:1176399164154851368>": contributors[0],
    "<:lap:1110862059647795240>": contributors[1],
    "<:balu:1110862230343397387>": contributors[2],
    "<:pizzacat:1110862947145760939>": contributors[3],
    "<:spag:1110866508017586187>": contributors[4],
    "<:gumbo:1145946572589383731>": contributors[5],
    "<:baguette:1113326206947954849>": contributors[6],
    "<:bagelface:1148723908556632205>": contributors[7],
    "<:breeze:1113744843575922708>": contributors[8],
    "<:ploxx:1154103719496003709>": contributors[9]
}