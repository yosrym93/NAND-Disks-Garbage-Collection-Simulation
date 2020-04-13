class PhysicalPage:
    FREE = 0
    VALID = 1
    INVALID = -1

    def __init__(self, physical_block):
        self.block = physical_block
        self.state = self.FREE
        self.logical_page = None

    def invalidate(self):
        self.state = self.INVALID
        self.block.invalid_pages_count += 1

    def allocate(self, logical_page):
        self.state = self.VALID
        self.logical_page = logical_page

    def free(self):
        self.state = self.FREE
        self.logical_page = None

    def is_valid(self):
        return self.state == self.VALID
