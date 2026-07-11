# Patch for memory/fact_schema.py
#
# Add this block inside init_fact_schema(), after entity_facts table creation.

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS entity_relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_entity_id INTEGER NOT NULL,
            to_entity_id INTEGER NOT NULL,
            predicate TEXT NOT NULL,
            fact_id INTEGER,
            confidence REAL DEFAULT 0.7,
            evidence TEXT,
            source TEXT,
            metadata_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(from_entity_id) REFERENCES entities(id),
            FOREIGN KEY(to_entity_id) REFERENCES entities(id),
            FOREIGN KEY(fact_id) REFERENCES facts(id)
        )
        """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_entity_relationships_from
        ON entity_relationships(from_entity_id)
        """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_entity_relationships_to
        ON entity_relationships(to_entity_id)
        """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_entity_relationships_predicate
        ON entity_relationships(predicate)
        """
    )

