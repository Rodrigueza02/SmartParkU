import psycopg

ORPHAN_TABLES = [
    "accesos", "espacios", "huella_carbono", "incidentes",
    "lecturas", "sanciones", "sensores", "vehiculos"
]

conn = psycopg.connect("postgresql://postgres:1138@localhost:5432/smartparku")
cur = conn.cursor()

for tname in ORPHAN_TABLES:
    print(f"\n{'='*60}")
    print(f"  TABLA: {tname}")
    print(f"{'='*60}")

    # Columnas + tipos + nullable + default
    cur.execute("""
        SELECT column_name, data_type, character_maximum_length,
               is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position;
    """, (tname,))
    cols = cur.fetchall()
    print("  COLUMNAS:")
    for c in cols:
        length = f"({c[2]})" if c[2] else ""
        print(f"    {c[0]:<25} {c[1]}{length:<20} nullable={c[3]}  default={c[4]}")

    # Primary keys
    cur.execute("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = 'public'
          AND tc.table_name = %s
        ORDER BY kcu.ordinal_position;
    """, (tname,))
    pks = cur.fetchall()
    print(f"  PRIMARY KEY: {[p[0] for p in pks]}")

    # Foreign keys (outgoing)
    cur.execute("""
        SELECT kcu.column_name,
               ccu.table_name AS foreign_table,
               ccu.column_name AS foreign_column,
               tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public'
          AND tc.table_name = %s;
    """, (tname,))
    fks = cur.fetchall()
    print(f"  FOREIGN KEYS (salientes):")
    if fks:
        for f in fks:
            print(f"    {f[0]} -> {f[1]}.{f[2]}  [{f[3]}]")
    else:
        print("    (ninguna)")

    # Foreign keys referencing this table (incoming)
    cur.execute("""
        SELECT tc.table_name AS source_table,
               kcu.column_name AS source_col,
               ccu.column_name AS ref_col,
               tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public'
          AND ccu.table_name = %s;
    """, (tname,))
    inc = cur.fetchall()
    print(f"  FOREIGN KEYS (entrantes — quién apunta aquí):")
    if inc:
        for i in inc:
            print(f"    {i[0]}.{i[1]} -> {tname}.{i[2]}  [{i[3]}]")
    else:
        print("    (ninguna)")

    # Indexes
    cur.execute("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = 'public' AND tablename = %s;
    """, (tname,))
    idxs = cur.fetchall()
    print(f"  ÍNDICES:")
    for ix in idxs:
        print(f"    {ix[0]}: {ix[1]}")

    # Row count
    cur.execute(f'SELECT COUNT(*) FROM "{tname}";')
    count = cur.fetchone()[0]
    print(f"  REGISTROS: {count}")

print(f"\n{'='*60}")
print("  RESUMEN")
print(f"{'='*60}")
print(f"{'TABLA':<20} {'REGISTROS':>10}  FK_OUT  FK_IN  RELACIONES")
for tname in ORPHAN_TABLES:
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public' AND tc.table_name = %s;
    """, (tname,))
    fk_out = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public' AND ccu.table_name = %s;
    """, (tname,))
    fk_in = cur.fetchone()[0]
    cur.execute(f'SELECT COUNT(*) FROM "{tname}";')
    count = cur.fetchone()[0]
    print(f"  {tname:<20} {count:>10}  {fk_out:>6}  {fk_in:>5}")

conn.close()
print("\nDone.")
