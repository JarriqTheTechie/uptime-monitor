
from ..masonite_audit import MasoniteAudit


class AuditProvider(MasoniteAudit):
    def __init__(self):
        self.observe()

    def boot(self):
        """Boots services required by the container."""
        pass
