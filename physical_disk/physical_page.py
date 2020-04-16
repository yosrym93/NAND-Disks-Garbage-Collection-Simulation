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
        self.update_frequency_time = 0

    def invalidate(self):
        self.state = self.INVALID
        self.block.invalid_pages_count += 1
        self.block.valid_pages_count -= 1

    def allocate(self, logical_page):
        self.state = self.VALID
        self.logical_page = logical_page
        self.block.valid_pages_count += 1

    def free(self):
        self.state = self.FREE
        self.logical_page = None

    def is_valid(self):
        return self.state == self.VALID

    def get_update_frequency_time(self, current_time):
        if self.logical_page.update_count > 0:
            self.update_frequency_time = (current_time - self.logical_page.allocation_time)\
                                         / self.logical_page.update_count
        else:
            self.update_frequency_time = (current_time - self.logical_page.allocation_time)
        return self.update_frequency_time


