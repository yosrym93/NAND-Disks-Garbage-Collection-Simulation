from abc import ABC, abstractmethod


class GarbageCollector(ABC):
    def __init__(self, physical_disk):
        self.physical_disk = physical_disk
        self.erase_operations_count = 0
        self.copy_operations_count = 0

    def run(self, current_psn):
        victim_block = self.get_victim_block(current_psn)
        if victim_block is not None:
            self.reallocate_block(victim_block)
            self.physical_disk.erase_block(victim_block)
            self.erase_operations_count += 1

    @abstractmethod
    def get_victim_block(self, current_psn):
        pass

    @abstractmethod
    def reallocate_block(self, victim_block):
        pass
