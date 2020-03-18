class PhysicalPage:
    FREE = 0
    VALID = 1
    INVALID = -1

    def __init__(self, physical_block):
        self.block = physical_block
        self.logical_page = None
        self.last_psn = 0
        self.state = self.FREE

    def allocate(self, logical_page):
        self.state = self.VALID
        self.logical_page = logical_page
        self.block.add_page_update_frequency(self.logical_page.update_frequency)

    def invalidate(self, physical_disk, current_psn):
        self.block.remove_page_update_frequency(self.logical_page.update_frequency)

        self.last_psn = current_psn
        self.state = self.INVALID
        self.logical_page = None

        if self.block.state != self.INVALID:
            self.block.state = self.INVALID
            physical_disk.valid_blocks_count -= 1

    def free(self):
        self.last_psn = 0
        self.state = self.FREE
        self.logical_page = None

    def is_valid(self):
        return self.state == self.VALID
