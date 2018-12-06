
class GraphObj:
    def __init__(self):
        #
        self.num_nodes = 0
        
        # Next Lyric ID to create
        self.next_lyric = 1
        
        # Map to access specific nodes
        self.node_map = {}
