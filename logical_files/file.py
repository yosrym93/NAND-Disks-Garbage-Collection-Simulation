from .logical_page import LogicalPage


class File:
    def __init__(self, pages_count, physical_disk, current_time):
        self.physical_disk = physical_disk
        self.logical_pages = []
        self.pages_count = pages_count
        for time, page in enumerate(range(pages_count), current_time):
            self.logical_pages.append(LogicalPage(physical_disk, time))

    def update_page(self, page_index, current_time):
        self.logical_pages[page_index].update(current_time)
