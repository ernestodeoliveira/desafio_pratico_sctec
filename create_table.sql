-- Script para criação da tabela empreendimentos no Supabase
-- Execute este SQL no SQL Editor do dashboard Supabase

CREATE TABLE IF NOT EXISTS empreendimentos (
    id BIGSERIAL PRIMARY KEY,
    nome_empreendimento VARCHAR(255) NOT NULL,
    nome_empreendedor VARCHAR(255) NOT NULL,
    municipio VARCHAR(100) NOT NULL,
    segmento VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'ativo',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para otimizar consultas com filtros
CREATE INDEX IF NOT EXISTS idx_empreendimentos_municipio ON empreendimentos(municipio);
CREATE INDEX IF NOT EXISTS idx_empreendimentos_segmento ON empreendimentos(segmento);
CREATE INDEX IF NOT EXISTS idx_empreendimentos_status ON empreendimentos(status);
