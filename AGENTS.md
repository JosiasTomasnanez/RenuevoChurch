## Propósito de este proyecto

Aplicación para administrar la base de datos de una iglesia (personas, ministerios, áreas, consolidación, CDB, etc.) con una estructura modular y fácil de extender.

## Arquitectura general

- **DB / Persistencia**
  - `src/backend/db/db.py`: helper `Database` (SQLite) + inicialización de esquema y migraciones.
  - Tablas clave:
    - `person`: datos personales + FKs a `address`, `consolidation`, `cdb`, etc.
    - `ministry`: catálogo de ministerios.
    - `ministry_area`: áreas que pertenecen a un ministerio (0..N por ministerio).
    - `person_ministry`: relación muchos-a-muchos entre personas y ministerios (opcionalmente con área y flag `is_primary`).
    - `person_occupation`, `address`, `consolidation`, `cdb`, etc.

- **Repositories (capa de acceso a datos)**
  - Carpeta: `src/backend/db/repositories/`
  - Patrones:
    - Un módulo por “tema”: `person_repository.py`, `config_repository.py`, `ministry_repository.py`, `person_ministry_repository.py`, etc.
    - No se usan objetos de dominio aquí: los repos retornan `dict` simples (o estructuras anidadas de dicts).
  - `__init__.py` re-exporta funciones para que otros módulos importen desde `src.backend.db.repositories`.

- **Services (lógica de negocio)**
  - Carpeta: `src/backend/services/`
  - Mapean dicts de repos a modelos tipados (`Person`, `Ministry`, `MinistryArea`, etc.).
  - Encapsulan reglas de negocio:
    - Búsquedas por nombre, barrio, ministerio.
    - Manejo de memberships (`person_ministry`):
      - `get_people_by_ministry(ministry_id)`
      - `get_memberships_for_person(person_id)`
      - `update_person_memberships(person_id, memberships)`

- **Models (dominio)**
  - Carpeta: `src/backend/models/`
  - `Person`:
    - Campos escalares (`first_name`, `dni`, etc.) + FKs.
    - Objetos anidados: `address`, `ministry`, `ministry_area`.
    - Campo `memberships`: lista opcional con todas las asignaciones a ministerios/áreas (para vistas más ricas).
  - `Ministry`, `MinistryArea`, `Address`, etc. en archivos separados.

- **Frontend (Tkinter)**
  - Vistas: `src/frontend/views/`
    - `search_person_view.py`: búsqueda de personas (tree con 1 fila por persona, filtros, panel de detalles de ministerios/áreas).
    - `add_person_view.py`: alta de persona, incluyendo editor de múltiples asignaciones a ministerios/áreas.
    - `modify_person_view.py`: modificación de persona + editor de asignaciones.
    - `config_view.py`: administración de catálogos (ministerios, áreas, consolidación, CDB).


## Convenciones y buenas prácticas

- **Modularidad**
  - Mantener separación clara:
    - DB helpers (`db.py`) no deben conocer detalles de UI.
    - Repositories solo manejan SQL y estructuras de datos simples.
    - Services contienen la lógica de negocio y devuelven modelos.
    - Controllers adaptan services a la UI.
    - Views solo manejan Tkinter (widgets, layout, eventos).

- **Nombres**
  - Tablas y columnas en inglés (`person`, `ministry_area`, `consolidation_id`), aunque la UI esté en español.
  - Módulos en snake_case, clases en PascalCase, funciones en snake_case.
  - Evitar abreviaturas ambiguas (salvo las ya establecidas: `cdb`).

- **Complejidad ciclomatica en UI**
  - Extraer helpers en las views cuando una función pasa de ~40–50 líneas.
  - Evitar if/else anidados profundos; preferir tempranos retornos y helpers.
  - No mezclar:
    - acceso a servicios,
    - transformación de datos,
    - actualización de widgets
    en un mismo bloque gigante; separar en métodos pequeños.

- **Shapes de datos**
  - Repositories devuelven dicts (posiblemente anidados).
  - Services convierten a modelos (`Person`, etc.) usando `from_dict`.
  - Views deben trabajar con modelos donde sea posible para reducir `.get(...)` repetidos.
  - Evitar mezclar dicts crudos y modelos en una misma función de UI.

## Reglas para ministerios / áreas / memberships

- Modelo conceptual:
  - Un `Ministry` puede tener 0..N `MinistryArea`.
  - Una persona puede:
    - estar en 0..N ministerios,
    - opcionalmente con un área específica por ministerio,
    - y tener 0 o 1 asignación marcada como “principal”.

- Base de datos:
  - `person.ministry_id` y `person.ministry_area_id` se consideran **campos de legado**.
  - La relación actual y oficial se guarda en `person_ministry`:
    - `person_id` (FK a `person`)
    - `ministry_id` (FK a `ministry`)
    - `area_id` (FK opcional a `ministry_area`)
    - `is_primary` (BOOLEAN)
  - Migraciones deben:
    - Crear `person_ministry` si no existe.
    - Copiar datos de `person.ministry_area_id` / `person.ministry_id` a `person_ministry` cuando sea necesario.

- Backend:
  - Repositorio `person_ministry_repository.py`:
    - `list_memberships_by_person(person_id)`
    - `set_memberships_for_person(person_id, memberships)`
    - `find_person_ids_by_ministry(ministry_id)`
  - Service `people`:
    - Usar `find_person_ids_by_ministry` en `get_people_by_ministry`.
    - Exponer:
      - `get_memberships_for_person(person_id)`
      - `update_person_memberships(person_id, memberships)`

- Frontend:
  - `SearchPersonFrame`:
    - Mantiene 1 fila por persona.
    - Usa un **panel de detalles** para listar todas las asignaciones (ministerio / área), marcando con `*` la principal.
    - El filtro por ministerio usa el servicio `get_people_by_ministry` para soportar múltiples asignaciones.
  - `AddPersonFrame` y `ModifyPersonFrame`:
    - Tienen un pequeño “editor de asignaciones”:
      - Combobox de ministerio.
      - Combobox de área dependiente (si ese ministerio tiene áreas).
      - Checkbox “Principal”.
      - Lista de asignaciones con botón “Quitar”.
    - Al guardar:
      - Envían los datos básicos de la persona vía `create_person` / `update_person`.
      - Llaman a `update_person_memberships` con la lista de memberships (solo claves y `is_primary`).
    - Los campos legacy (`person.ministry_id`, `person.ministry_area_id`) se mantienen en `None` en nuevas operaciones.

## Migraciones SQLite en este repo

- Las migraciones se implementan en `Database._apply_migrations` (`src/backend/db/db.py`).
- Reglas:
  - Siempre usar `CREATE TABLE IF NOT EXISTS` para nuevas tablas.
  - Para nuevas columnas:
    - primero revisar con `PRAGMA table_info` si ya existen,
    - solo entonces ejecutar `ALTER TABLE`.
  - Los bloques de migración deben ir envueltos en `try/except` y nunca impedir que la app arranque.
  - Mantener las migraciones **idempotentes** (que se puedan ejecutar más de una vez sin error).

- Flujo típico:
  - Agregar/ajustar el esquema base en `_get_schema_statements`.
  - Agregar lógica de migración en `_apply_migrations` para bases ya existentes.
  - Probar ejecutando el script principal de `db.py` o arrancando la app.

## Guía de refactor y tests manuales

- Antes de tocar código:
  - Identificar si el cambio afecta:
    - solo UI,
    - solo backend,
    - o ambos.
  - Si afecta estructura de datos (tablas, modelos, payloads), documentarlo en este archivo.

- Al refactorizar UI:
  - Mantener `SearchPersonFrame`, `AddPersonFrame`, `ModifyPersonFrame` y `ConfigurationFrame` libres de lógica de negocio pesada.
  - Preferir helpers privados (_métodos `def _algo(...)`) para partes repetidas o ramas complejas.

- Tests manuales mínimos después de cambios en personas/ministerios:
  1. Crear persona con:
     - 1 ministerio sin área.
     - 1 ministerio distinto con área.
  2. Ver en búsqueda:
     - que aparece una sola fila,
     - que el panel de detalles lista todas las asignaciones,
     - que la principal está marcada con `*`.
  3. Filtrar por cada ministerio:
     - la persona debe aparecer en ambos filtros si tiene ambas asignaciones.
  4. Modificar persona:
     - agregar/quitar asignaciones,
     - cambiar cuál es principal,
     - guardar y verificar en búsqueda y en la vista de modificación.

Seguir estas reglas ayuda a mantener el proyecto profesional, modular y fácil de entender para futuros cambios (tanto tuyos como de cualquier colaborador o agente). 

