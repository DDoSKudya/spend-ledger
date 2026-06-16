from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.deps import increment_sql_count


def attach_sql_counter(engine: Engine) -> None:
    @event.listens_for(engine, "before_cursor_execute")
    def _count_query(
        _conn,
        _cursor,
        _statement,
        _parameters,
        _context,
        _executemany,
    ) -> None:
        increment_sql_count()
