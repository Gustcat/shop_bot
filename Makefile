include .env

DB_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
ALEMBIC_DIR = alembic

init_alembic:
	echo ${DB_URL}
	@if [ ! -d ${ALEMBIC_DIR} ]; then \
		alembic init ${ALEMBIC_DIR}; \
	fi
	@sed -i "s|^sqlalchemy.url = .*|sqlalchemy.url = ${DB_URL}|" alembic.ini
