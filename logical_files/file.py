from .logical_page import LogicalPage


class File:
    def __init__(self, pages_count, physical_disk, current_psn):
        self.physical_disk = physical_disk
        self.logical_pages = []
        self.pages_count = pages_count
        for page in range(pages_count):
            self.logical_pages.append(LogicalPage(physical_disk, current_psn))
            current_psn += 1

    def update_page(self, page_index, psn):
        self.logical_pages[page_index].update(psn, self.physical_disk)
