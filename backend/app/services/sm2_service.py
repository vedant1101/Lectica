from datetime import datetime, timedelta
from app.models.models import Flashcard


class SM2Service:

    def review(self, card: Flashcard, quality: int) -> Flashcard:
        assert 0 <= quality <= 5

        if quality >= 3:
            if card.repetitions == 0:
                card.interval = 1
            elif card.repetitions == 1:
                card.interval = 6
            else:
                card.interval = round(card.interval * card.ease_factor)
            card.repetitions += 1
        else:
            card.repetitions = 0
            card.interval = 1

        card.ease_factor = max(
            1.3,
            card.ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        )

        card.last_reviewed = datetime.utcnow()
        card.due_date = datetime.utcnow() + timedelta(days=card.interval)

        return card