class BaseBadge(object):
    def eligible(self, relationship):
        return relationship.badge_set.filter(name=self.name).exists()

class ContactBadge(BaseBadge):
    karma_award = 1
    name = "Contact"
    description = "Each user write one message to each other"

    def eligible(self, relatinship):
        el = super(ChattingBadge, self).eligible(relationship)
        lines1 = relationship.user1_stats.my_total_lines
        lines2 = relationship.user2_stats.my_total_lines
        return lines1 > 0 and lines2 > 0

class ChattingBadge(BaseBadge):
    karma_award = 10
    name = "Chatting"
    description = "Each user writes 10 messages to each other"

    def eligible(self, relationship):
        el = super(ChattingBadge, self).eligible(relationship)
        lines1 = relationship.user1_stats.my_total_lines
        lines2 = relationship.user2_stats.my_total_lines
        return el and lines1 > 10 and lines2 > 10

def DaySpanBadge(BaseBadge):
    karma_award = 20
    name = "Day Span"
    description = "24 hours lapse between messages"

    def eligible(self, relationship):
        lines1 = relationship.user1_stats.my_total_lines
        lines2 = relationship.user2_stats.my_total_lines

BADGES = [ContactBadge, ChattingBadge, DaySpanBadge]