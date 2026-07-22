import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import pandas as pd
from typing import Optional, List, Dict, Any
import logging

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import config

logger = logging.getLogger(__name__)
Base = declarative_base()


class DatabaseManager:
    def __init__(self):
        self.config = config.db
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()

    def _initialize_engine(self):
        try:
            self.engine = create_engine(
                self.config.connection_string,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=False
            )
            self.SessionLocal = sessionmaker(bind=self.engine)
            logger.info("Database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise

    def create_database(self):
        try:
            conn = pymysql.connect(
                host=self.config.HOST,
                port=self.config.PORT,
                user=self.config.USER,
                password=self.config.PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {self.config.DATABASE} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Database '{self.config.DATABASE}' created/verified")
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            raise

    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        try:
            with self.engine.connect() as conn:
                result = pd.read_sql(text(query), conn, params=params)
            return result
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise

    def execute_insert(self, query: str, params: Optional[tuple] = None):
        try:
            with self.engine.connect() as conn:
                conn.execute(text(query), params)
                conn.commit()
        except Exception as e:
            logger.error(f"Insert execution error: {e}")
            raise

    def execute_many(self, query: str, data: List[tuple]):
        try:
            with self.engine.connect() as conn:
                conn.execute(text(query), data)
                conn.commit()
        except Exception as e:
            logger.error(f"Batch insert error: {e}")
            raise

    def table_exists(self, table_name: str) -> bool:
        query = (
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = :db AND table_name = :table"
        )
        result = self.execute_query(query, {"db": self.config.DATABASE, "table": table_name})
        return result.iloc[0, 0] > 0

    def create_tables(self):
        self.create_database()
        Base.metadata.create_all(bind=self.engine)
        logger.info("All tables created/verified")

    def drop_tables(self):
        Base.metadata.drop_all(bind=self.engine)
        logger.info("All tables dropped")


db_manager = DatabaseManager()
