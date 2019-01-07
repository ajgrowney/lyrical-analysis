
class GraphObj:
    def __init__(self):
        # Map for the Artist Search Menu {name: id}
        self.artist_choices = {}        
        # Map to access specific nodes {id: NodeObject}
        self.node_map = {}
        # Maps Song ID to Title {id: title}
        self.song_id_title = {}
