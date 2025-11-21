-- Check Foreign Keys to 'users' table
-- This script diagnoses all FK relationships involving user references

\echo '=== FKs que REFERENCIAN a "users" (correcto) ==='
SELECT
  tc.constraint_name,
  tc.table_name    AS src_table,
  kcu.column_name  AS src_column,
  ccu.table_name   AS ref_table,
  ccu.column_name  AS ref_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
  ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND ccu.table_name = 'users'
  AND tc.table_schema = 'public'
ORDER BY src_table, constraint_name;

\echo ''
\echo '=== FKs que TODAVÍA apuntan a "usuarios" (LEGADO - necesita fix) ==='
SELECT
  tc.constraint_name,
  tc.table_name    AS src_table,
  kcu.column_name  AS src_column,
  ccu.table_name   AS ref_table,
  ccu.column_name  AS ref_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
  ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND ccu.table_name = 'usuarios'
  AND tc.table_schema = 'public'
ORDER BY src_table, constraint_name;

\echo ''
\echo '=== Tablas que existen (users vs usuarios) ==='
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND (table_name = 'users' OR table_name = 'usuarios')
ORDER BY table_name;

