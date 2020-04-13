class PhysicalPage:
    FREE = 0
    VALID = 1
    INVALID = -1

    def __init__(self, physical_block):
        self.block = physical_block
        self.state = self.FREE
        self.logical_page = None
        self.time_invalid = None
        self.piu = 0
        self.last_update = 0

    def invalidate(self, current_time):
        self.state = self.INVALID
        self.time_invalid = current_time
        self.block.invalid_pages_count += 1

    def allocate(self, logical_page, current_time):
        self.state = self.VALID
        self.last_update = current_time
        self.logical_page = logical_page

    def free(self):
        self.state = self.FREE
        self.logical_page = None

    def is_valid(self):
        return self.state == self.VALID
