from abc import ABC, abstractmethod


class GarbageCollector(ABC):
    def __init__(self, physical_disk):
        self.physical_disk = physical_disk
        self.erase_operations_count = 0
        self.copy_operations_count = 0

    def run(self, current_time):
        if self.is_gc_needed():
            victim_block = self.get_victim_block(current_time)
            self.reallocate_block(victim_block)
            self.physical_disk.erase_block(victim_block)
            self.erase_operations_count += 1

    @abstractmethod
    def is_gc_needed(self):
        pass

    @abstractmethod
    def get_victim_block(self, current_time):
        pass

    @abstractmethod
    def reallocate_block(self, victim_block):
        pass
