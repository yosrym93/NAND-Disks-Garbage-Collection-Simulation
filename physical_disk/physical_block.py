from config import *
from .physical_page import PhysicalPage


class PhysicalBlock:
    FREE = 0
    VALID = 1
    INVALID = -1

    def __init__(self):
        self.erase_count = 0
        self.valid_pages_count = 0
        self.free_pages_count = pages_per_block
        self.state = self.FREE
        self.pages = []
        self.free_pages = list(range(pages_per_block))
        self.average_update_frequency = 0
        for page in range(pages_per_block):
            self.pages.append(PhysicalPage(physical_block=self))

    def get_free_page(self):
        free_page = self.pages[self.free_pages.pop()]
        self.free_pages_count -= 1
        if self.state == self.FREE:
            self.state = self.VALID
        return free_page

    def get_cps(self, current_psn):
        cps = 0
        for page in self.pages:
            if page.state == self.INVALID:
                cps += current_psn - page.last_psn
        return cps

    def erase(self):
        self.average_update_frequency = 0
        self.free_pages_count = pages_per_block
        self.valid_pages_count = 0
        self.free_pages = list(range(pages_per_block))
        self.state = self.FREE
        self.erase_count += 1
        for page in self.pages:
            if page.state != page.FREE:
                page.free()

    def add_page_update_frequency(self, update_frequency):
        self.average_update_frequency = (self.average_update_frequency * self.valid_pages_count
                                         + update_frequency) / (self.valid_pages_count+1)
        self.valid_pages_count += 1

    def remove_page_update_frequency(self, update_frequency):
        if self.valid_pages_count == 1:
            self.average_update_frequency = 0
        else:
            self.average_update_frequency = (self.average_update_frequency * self.valid_pages_count
                                             - update_frequency) / (self.valid_pages_count-1)
        self.valid_pages_count -= 1
