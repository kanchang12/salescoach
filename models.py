"""
Love2Learn — Database Models
"""

import os
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")


def _migrate(db):
    """Add missing columns to existing tables without dropping data."""
    migrations = [
        ("learning_sessions", "leo_phase",           "VARCHAR(20)  DEFAULT 'rapport'"),
        ("learning_sessions", "leo_msgs_in_phase",   "INTEGER      DEFAULT 0"),
        ("learning_sessions", "leo_we_do_attempts",  "INTEGER      DEFAULT 0"),
        ("learning_sessions", "leo_rapport_done",    "BOOLEAN      DEFAULT FALSE"),
        ("learning_sessions", "leo_current_unit",    "VARCHAR(50)"),
        ("learning_sessions", "leo_concepts_covered","JSONB"),
        ("learning_sessions", "leo_question_idx",    "INTEGER      DEFAULT 0"),
    ]
    try:
        with db.engine.connect() as conn:
            for table, col, defn in migrations:
                try:
                    conn.execute(db.text(
                        f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {defn}"
                    ))
                    conn.commit()
                except Exception:
                    conn.rollback()
    except Exception as e:
        print(f"[MIGRATE] {e}")


def _create_new_tables(db):
    """
    Create new tables that may not exist yet using IF NOT EXISTS.
    Safe to run on every deploy — never fails if table already exists.
    """
    statements = [
        """CREATE TABLE IF NOT EXISTS question_bank (
            id SERIAL PRIMARY KEY,
            unit_id VARCHAR(50) NOT NULL,
            subject VARCHAR(20) NOT NULL,
            year_group VARCHAR(10) NOT NULL,
            phase VARCHAR(10) NOT NULL,
            question_text TEXT NOT NULL,
            answer_guide TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )""",
        "CREATE INDEX IF NOT EXISTS ix_question_bank_unit_id ON question_bank (unit_id)",
        """CREATE TABLE IF NOT EXISTS session_summaries (
            id SERIAL PRIMARY KEY,
            child_id INTEGER NOT NULL REFERENCES children(id),
            session_id VARCHAR(50) NOT NULL UNIQUE,
            subject VARCHAR(20),
            year_group VARCHAR(10),
            unit_id VARCHAR(50),
            unit_name VARCHAR(200),
            phase_reached VARCHAR(20),
            units_covered JSONB DEFAULT '[]',
            active_minutes INTEGER DEFAULT 0,
            went_well TEXT,
            struggled_with TEXT,
            next_unit_id VARCHAR(50),
            next_unit_name VARCHAR(200),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )""",
        "CREATE INDEX IF NOT EXISTS ix_session_summaries_child_id ON session_summaries (child_id)",
        """CREATE TABLE IF NOT EXISTS curriculum (
            id SERIAL PRIMARY KEY,
            unit_id VARCHAR(50) UNIQUE NOT NULL,
            subject VARCHAR(20) NOT NULL,
            year_group VARCHAR(10) NOT NULL,
            topic_name VARCHAR(200) NOT NULL,
            nc_objective TEXT,
            leo_intro TEXT NOT NULL,
            difficulty INTEGER DEFAULT 1,
            examples JSONB DEFAULT '{}',
            check_questions JSONB DEFAULT '{}',
            common_mistakes JSONB DEFAULT '[]',
            unit_order INTEGER DEFAULT 0
        )""",
        "CREATE INDEX IF NOT EXISTS ix_curriculum_subject ON curriculum (subject)",
        "CREATE INDEX IF NOT EXISTS ix_curriculum_year ON curriculum (year_group)",
        """CREATE TABLE IF NOT EXISTS child_coverage (
            id SERIAL PRIMARY KEY,
            child_id INTEGER NOT NULL REFERENCES children(id),
            unit_id VARCHAR(50) NOT NULL,
            subject VARCHAR(20) NOT NULL,
            year_group VARCHAR(10) NOT NULL,
            times_practiced INTEGER DEFAULT 1,
            struggle_count INTEGER DEFAULT 0,
            mastery_level VARCHAR(20) DEFAULT 'learning',
            last_practiced TIMESTAMPTZ DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(child_id, unit_id)
        )""",
        "CREATE INDEX IF NOT EXISTS ix_child_coverage_child ON child_coverage (child_id)",
    ]
    try:
        with db.engine.connect() as conn:
            for stmt in statements:
                try:
                    conn.execute(db.text(stmt))
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    print(f"[DB] table/index stmt skipped (likely exists): {e}")
    except Exception as e:
        print(f"[DB] _create_new_tables: {e}")



def seed_curriculum(db):
    """Seed curriculum table from curriculum.py — runs once, skips if already seeded."""
    try:
        if db.session.execute(db.text("SELECT COUNT(*) FROM curriculum")).scalar() > 0:
            return  # Already seeded
    except Exception:
        return  # Table doesn't exist yet, create_new_tables will handle it

    try:
        import curriculum as cur, json
        order = 0
        for year in ['year_2','year_3','year_4','year_5','year_6']:
            for subj in ['maths','reading','coding']:
                topics = cur.get_curriculum(year, subj)
                diff_map = {'year_2':1,'year_3':1,'year_4':2,'year_5':3,'year_6':3}
                for t in topics:
                    row = Curriculum(
                        unit_id=t['id'], subject=subj, year_group=year,
                        topic_name=t['topic'],
                        nc_objective=t.get('nc_objective',''),
                        leo_intro=t.get('leo_intro',''),
                        difficulty=diff_map.get(year,1),
                        examples=t.get('examples',{}),
                        check_questions=t.get('check_questions',{}),
                        common_mistakes=t.get('common_mistakes',[]),
                        unit_order=order,
                    )
                    db.session.add(row)
                    order += 1
        db.session.commit()
        print(f"[CURRICULUM] Seeded {order} units")
    except Exception as e:
        print(f"[CURRICULUM] Seed failed: {e}")
        db.session.rollback()


def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[DB] create_all skipped (tables exist): {e}")
        _create_new_tables(db)
        _migrate(db)
        seed_curriculum(db)


class Parent(db.Model):
    __tablename__ = 'parents'
    id                      = db.Column(db.Integer, primary_key=True)
    email                   = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name                    = db.Column(db.String(255), nullable=False)
    password_hash           = db.Column(db.String(255), nullable=False)
    salt                    = db.Column(db.String(64), nullable=False)
    plan                    = db.Column(db.String(20), default='trial')
    trial_started_at        = db.Column(db.DateTime(timezone=True), nullable=True)
    trial_ends_at           = db.Column(db.DateTime(timezone=True), nullable=True)
    subscription_start      = db.Column(db.DateTime(timezone=True), nullable=True)
    subscription_end        = db.Column(db.DateTime(timezone=True), nullable=True)
    dashboard_password_hash = db.Column(db.String(255), nullable=True)
    gdpr_consent            = db.Column(db.Boolean, default=False)
    gdpr_consent_at         = db.Column(db.DateTime(timezone=True), nullable=True)
    data_deletion_requested = db.Column(db.Boolean, default=False)
    created_at              = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login              = db.Column(db.DateTime(timezone=True), nullable=True)
    is_active               = db.Column(db.Boolean, default=True)
    children = db.relationship('Child', backref='parent', lazy='dynamic', cascade='all, delete-orphan')

    def can_access(self):
        now = datetime.now(timezone.utc)
        if self.plan == 'trial':
            return bool(self.trial_ends_at and now < self.trial_ends_at)
        if self.plan in ('connect', 'essentials'):
            return bool(self.subscription_end and now < self.subscription_end)
        return False

    def can_view_dashboard(self):
        import datetime as dt
        if self.plan == 'connect':
            return True
        return dt.date.today().weekday() == 6


class Child(db.Model):
    __tablename__ = 'children'
    id                    = db.Column(db.Integer, primary_key=True)
    parent_email          = db.Column(db.String(255), db.ForeignKey('parents.email'), nullable=False, index=True)
    first_name            = db.Column(db.String(100), nullable=False)
    year_group            = db.Column(db.String(10), nullable=False)
    interests             = db.Column(db.JSON, default=dict)
    diamond_balance       = db.Column(db.Integer, default=0)
    total_diamonds_earned = db.Column(db.Integer, default=0)
    current_streak        = db.Column(db.Integer, default=0)
    longest_streak        = db.Column(db.Integer, default=0)
    last_login_date       = db.Column(db.Date, nullable=True)
    preferred_login_time  = db.Column(db.Time, nullable=True)
    created_at            = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active           = db.Column(db.DateTime(timezone=True), nullable=True)
    sessions  = db.relationship('LearningSession',    backref='child', lazy='dynamic', cascade='all, delete-orphan')
    diamonds  = db.relationship('DiamondTransaction', backref='child', lazy='dynamic', cascade='all, delete-orphan')
    absences  = db.relationship('AbsenceRecord',      backref='child', lazy='dynamic', cascade='all, delete-orphan')


class Admin(db.Model):
    __tablename__ = 'admins'
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name          = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    salt          = db.Column(db.String(64), nullable=False)
    created_at    = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login    = db.Column(db.DateTime(timezone=True), nullable=True)


class LearningSession(db.Model):
    __tablename__ = 'learning_sessions'
    id               = db.Column(db.Integer, primary_key=True)
    session_id       = db.Column(db.String(50), unique=True, nullable=False, index=True)
    child_id         = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False, index=True)
    session_type     = db.Column(db.String(20), default='maths')
    year_group       = db.Column(db.String(10))
    interest_context = db.Column(db.String(100))
    started_at       = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_saved_at    = db.Column(db.DateTime(timezone=True), nullable=True)
    active_minutes   = db.Column(db.Integer, default=0)
    status           = db.Column(db.String(20), default='in_progress')

    # Leo phase — plain columns, no JSON mutation
    leo_phase          = db.Column(db.String(20), default='rapport')
    leo_msgs_in_phase  = db.Column(db.Integer, default=0)
    leo_we_do_attempts = db.Column(db.Integer, default=0)
    leo_rapport_done   = db.Column(db.Boolean, default=False)
    leo_current_unit   = db.Column(db.String(50), nullable=True)
    leo_concepts_covered = db.Column(db.JSON, default=list)
    leo_question_idx   = db.Column(db.Integer, default=0)

    # Curriculum tracking
    unit_id          = db.Column(db.String(50), nullable=True)
    unit_name        = db.Column(db.String(200), nullable=True)
    phase_reached    = db.Column(db.String(20), nullable=True)

    # Effort + accuracy
    questions_asked  = db.Column(db.Integer, default=0)
    questions_by_leo = db.Column(db.Integer, default=0)
    child_questions  = db.Column(db.Integer, default=0)
    restarts         = db.Column(db.Integer, default=0)
    correct_easy     = db.Column(db.Integer, default=0)
    correct_medium   = db.Column(db.Integer, default=0)
    correct_hard     = db.Column(db.Integer, default=0)
    attempted_easy   = db.Column(db.Integer, default=0)
    attempted_medium = db.Column(db.Integer, default=0)
    attempted_hard   = db.Column(db.Integer, default=0)

    # Diamonds + behaviour
    diamonds_earned  = db.Column(db.Integer, default=0)
    star_rating      = db.Column(db.Integer, nullable=True)
    behaviour_flags  = db.Column(db.JSON, default=list)
    homework_set     = db.Column(db.Text, nullable=True)

    # Full transcript
    chat_log         = db.Column(db.JSON, default=list)


class QuestionBank(db.Model):
    """Pre-generated practice questions. Leo reads one per turn — no content overload."""
    __tablename__ = 'question_bank'
    id            = db.Column(db.Integer, primary_key=True)
    unit_id       = db.Column(db.String(50), nullable=False, index=True)
    subject       = db.Column(db.String(20), nullable=False)
    year_group    = db.Column(db.String(10), nullable=False)
    phase         = db.Column(db.String(10), nullable=False)   # we_do | you_do
    question_text = db.Column(db.Text, nullable=False)
    answer_guide  = db.Column(db.Text, nullable=True)
    created_at    = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SessionSummary(db.Model):
    """Written at end of session. Leo reads this at the START of the next one."""
    __tablename__ = 'session_summaries'
    id             = db.Column(db.Integer, primary_key=True)
    child_id       = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False, index=True)
    session_id     = db.Column(db.String(50), nullable=False, unique=True)
    subject        = db.Column(db.String(20))
    year_group     = db.Column(db.String(10))
    unit_id        = db.Column(db.String(50))
    unit_name      = db.Column(db.String(200))
    phase_reached  = db.Column(db.String(20))
    units_covered  = db.Column(db.JSON, default=list)
    active_minutes = db.Column(db.Integer, default=0)
    went_well      = db.Column(db.Text, nullable=True)
    struggled_with = db.Column(db.Text, nullable=True)
    next_unit_id   = db.Column(db.String(50), nullable=True)
    next_unit_name = db.Column(db.String(200), nullable=True)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))



class Curriculum(db.Model):
    """All curriculum content in DB. Seeded once from curriculum.py. Leo queries this."""
    __tablename__ = 'curriculum'
    id              = db.Column(db.Integer, primary_key=True)
    unit_id         = db.Column(db.String(50), unique=True, nullable=False, index=True)
    subject         = db.Column(db.String(20), nullable=False, index=True)
    year_group      = db.Column(db.String(10), nullable=False, index=True)
    topic_name      = db.Column(db.String(200), nullable=False)
    nc_objective    = db.Column(db.Text, nullable=True)
    leo_intro       = db.Column(db.Text, nullable=False)
    difficulty      = db.Column(db.Integer, default=1)
    examples        = db.Column(db.JSON, default=dict)   # {interest: example_text}
    check_questions = db.Column(db.JSON, default=dict)   # {interest: question_text}
    common_mistakes = db.Column(db.JSON, default=list)   # [mistake_string]
    unit_order      = db.Column(db.Integer, default=0)


class ChildCoverage(db.Model):
    """Tracks per-child coverage of every curriculum unit across all sessions."""
    __tablename__ = 'child_coverage'
    id              = db.Column(db.Integer, primary_key=True)
    child_id        = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False, index=True)
    unit_id         = db.Column(db.String(50), nullable=False, index=True)
    subject         = db.Column(db.String(20), nullable=False)
    year_group      = db.Column(db.String(10), nullable=False)
    times_practiced = db.Column(db.Integer, default=1)
    struggle_count  = db.Column(db.Integer, default=0)
    mastery_level   = db.Column(db.String(20), default='learning')  # learning/practiced/mastered
    last_practiced  = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at      = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('child_id', 'unit_id', name='uq_child_unit'),)


class DiamondTransaction(db.Model):
    __tablename__ = 'diamond_transactions'
    id            = db.Column(db.Integer, primary_key=True)
    child_id      = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False, index=True)
    session_id    = db.Column(db.String(50), nullable=True)
    amount        = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    reason        = db.Column(db.String(50), nullable=False)
    description   = db.Column(db.String(255))
    created_at    = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'amount': self.amount,
            'balance_after': self.balance_after,
            'reason': self.reason,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else '',
        }


class DiamondGoal(db.Model):
    __tablename__ = 'diamond_goals'
    id                = db.Column(db.Integer, primary_key=True)
    child_id          = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False, index=True)
    parent_email      = db.Column(db.String(255), nullable=False)
    target_diamonds   = db.Column(db.Integer, nullable=False)
    treat_description = db.Column(db.String(255), nullable=False)
    week_start        = db.Column(db.Date, nullable=False)
    week_end          = db.Column(db.Date, nullable=False)
    diamonds_at_start = db.Column(db.Integer, default=0)
    is_active         = db.Column(db.Boolean, default=True)
    achieved          = db.Column(db.Boolean, default=False)
    created_at        = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AbsenceRecord(db.Model):
    __tablename__ = 'absence_records'
    id               = db.Column(db.Integer, primary_key=True)
    child_id         = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False, index=True)
    absent_date      = db.Column(db.Date, nullable=False)
    reason_given     = db.Column(db.Text, nullable=True)
    assessment       = db.Column(db.String(30), nullable=True)
    diamonds_awarded = db.Column(db.Integer, default=0)
    responded_at     = db.Column(db.DateTime(timezone=True), nullable=True)


class DailyProgress(db.Model):
    __tablename__ = 'daily_progress'
    id              = db.Column(db.Integer, primary_key=True)
    child_id        = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False, index=True)
    date            = db.Column(db.Date, nullable=False)
    active_minutes  = db.Column(db.Integer, default=0)
    diamonds_earned = db.Column(db.Integer, default=0)
    streak          = db.Column(db.Integer, default=0)
    questions_asked = db.Column(db.Integer, default=0)
    correct_easy    = db.Column(db.Integer, default=0)
    correct_medium  = db.Column(db.Integer, default=0)
    correct_hard    = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'active_minutes': self.active_minutes,
            'diamonds_earned': self.diamonds_earned,
            'streak': self.streak,
            'questions_asked': self.questions_asked,
            'correct_easy': self.correct_easy,
            'correct_medium': self.correct_medium,
            'correct_hard': self.correct_hard,
        }


class BetaFeedback(db.Model):
    __tablename__ = 'beta_feedback'
    id             = db.Column(db.Integer, primary_key=True)
    parent_email   = db.Column(db.String(255), nullable=False)
    child_name     = db.Column(db.String(100))
    rating         = db.Column(db.Integer)
    what_worked    = db.Column(db.Text)
    what_didnt     = db.Column(db.Text)
    would_pay      = db.Column(db.String(20))
    other_comments = db.Column(db.Text)
    created_at     = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
