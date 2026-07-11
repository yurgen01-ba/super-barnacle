from memory.db import get_connection


def init_fact_schema():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            fact_type TEXT NOT NULL DEFAULT 'unknown',
            confidence REAL NOT NULL DEFAULT 0.7,
            status TEXT NOT NULL DEFAULT 'proposed',
            evidence TEXT,
            source TEXT,
            metadata_json TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_predicate ON facts(predicate)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_type ON facts(fact_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_source ON facts(source)")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fact_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact_id INTEGER NOT NULL,
            evidence_type TEXT,
            evidence_ref TEXT,
            quote TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(fact_id) REFERENCES facts(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            entity_type TEXT DEFAULT 'unknown',
            description TEXT,
            metadata_json TEXT,
            confidence REAL DEFAULT 0.7,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entity_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL,
            fact_id INTEGER NOT NULL,
            relation_type TEXT DEFAULT 'about',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(entity_id) REFERENCES entities(id),
            FOREIGN KEY(fact_id) REFERENCES facts(id)
        )
    """)

    cur.execute("""
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
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_entity_relationships_from ON entity_relationships(from_entity_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_entity_relationships_to ON entity_relationships(to_entity_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_entity_relationships_predicate ON entity_relationships(predicate)")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS entity_ontology (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL UNIQUE,
            ontology_type TEXT NOT NULL DEFAULT 'unknown',
            confidence REAL NOT NULL DEFAULT 0.3,
            classification_method TEXT DEFAULT 'heuristic',
            reason TEXT,
            metadata_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(entity_id) REFERENCES entities(id)
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_entity_ontology_type ON entity_ontology(ontology_type)")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS domain_objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT,
            object_type TEXT DEFAULT 'business_object',
            attributes_json TEXT,
            relationships_json TEXT,
            rules_json TEXT,
            lifecycle_json TEXT,
            evidence_json TEXT,
            confidence REAL DEFAULT 0.7,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(entity_id) REFERENCES entities(id)
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_domain_objects_name ON domain_objects(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_domain_objects_type ON domain_objects(object_type)")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS actors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            actor_type TEXT DEFAULT 'unknown',
            description TEXT,
            responsibilities_json TEXT,
            owned_objects_json TEXT,
            participates_in_json TEXT,
            interactions_json TEXT,
            permissions_json TEXT,
            evidence_json TEXT,
            confidence REAL DEFAULT 0.7,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(entity_id) REFERENCES entities(id)
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_actors_name ON actors(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_actors_type ON actors(actor_type)")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS processes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            process_type TEXT DEFAULT 'business_process',
            goal TEXT,
            participants_json TEXT,
            business_objects_json TEXT,
            steps_json TEXT,
            inputs_json TEXT,
            outputs_json TEXT,
            rules_json TEXT,
            exceptions_json TEXT,
            evidence_json TEXT,
            confidence REAL DEFAULT 0.7,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_processes_name ON processes(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_processes_type ON processes(process_type)")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'Project Summary',
            summary TEXT,
            metadata_json TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

