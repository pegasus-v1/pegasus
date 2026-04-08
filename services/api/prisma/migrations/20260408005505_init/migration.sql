-- CreateTable
CREATE TABLE "clanes" (
    "id" SERIAL NOT NULL,
    "nombre" VARCHAR(50) NOT NULL,
    "hora_entrada" TIME NOT NULL,
    "hora_salida" TIME NOT NULL,
    "tiempo_alimentacion_minutos" INTEGER NOT NULL,

    CONSTRAINT "clanes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "team_leaders" (
    "id" SERIAL NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "correo" VARCHAR(100) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "rol" VARCHAR(50) NOT NULL,
    "clan_id" INTEGER NOT NULL,

    CONSTRAINT "team_leaders_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "coder" (
    "id" SERIAL NOT NULL,
    "cedula" VARCHAR(20) NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "moodle_id" INTEGER NOT NULL,
    "clan_id" INTEGER NOT NULL,

    CONSTRAINT "coder_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "correos_enviados" (
    "id" SERIAL NOT NULL,
    "coder_id" INTEGER NOT NULL,
    "tipo_correo" VARCHAR(50) NOT NULL DEFAULT 'ausencia',
    "estado" VARCHAR(20) NOT NULL,
    "fecha_envio" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "correos_enviados_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "registros" (
    "id" SERIAL NOT NULL,
    "coder_id" INTEGER NOT NULL,
    "fecha" DATE NOT NULL,
    "hora" TIME NOT NULL,
    "estado_acceso" VARCHAR(20) NOT NULL,

    CONSTRAINT "registros_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "clanes_nombre_key" ON "clanes"("nombre");

-- CreateIndex
CREATE UNIQUE INDEX "team_leaders_correo_key" ON "team_leaders"("correo");

-- CreateIndex
CREATE UNIQUE INDEX "coder_cedula_key" ON "coder"("cedula");

-- CreateIndex
CREATE UNIQUE INDEX "coder_moodle_id_key" ON "coder"("moodle_id");

-- AddForeignKey
ALTER TABLE "team_leaders" ADD CONSTRAINT "team_leaders_clan_id_fkey" FOREIGN KEY ("clan_id") REFERENCES "clanes"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "coder" ADD CONSTRAINT "coder_clan_id_fkey" FOREIGN KEY ("clan_id") REFERENCES "clanes"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "correos_enviados" ADD CONSTRAINT "correos_enviados_coder_id_fkey" FOREIGN KEY ("coder_id") REFERENCES "coder"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "registros" ADD CONSTRAINT "registros_coder_id_fkey" FOREIGN KEY ("coder_id") REFERENCES "coder"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
