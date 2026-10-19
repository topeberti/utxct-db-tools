--
-- PostgreSQL database dump
--

\restrict GKAu0OOg2fgEA0zY9yvdbRZYZLR91o6rlY6YQzpkNBVhWEDjPPJ16QhIZfSoW8E

-- Dumped from database version 17.11 (Ubuntu 17.11-1.pgdg24.04+2)
-- Dumped by pg_dump version 18.6 (Ubuntu 18.6-1.pgdg24.04+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: meta; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA meta;


ALTER SCHEMA meta OWNER TO postgres;

--
-- Name: pgagent; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA pgagent;


ALTER SCHEMA pgagent OWNER TO postgres;

--
-- Name: SCHEMA pgagent; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA pgagent IS 'pgAgent system tables';


--
-- Name: data_type_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.data_type_enum AS ENUM (
    'uint8',
    'uint16',
    'float32',
    'float64'
);


ALTER TYPE public.data_type_enum OWNER TO postgres;

--
-- Name: file_type_enum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.file_type_enum AS ENUM (
    'tiff',
    'raw',
    'jpeg',
    'png'
);


ALTER TYPE public.file_type_enum OWNER TO postgres;

--
-- Name: studydirection; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.studydirection AS ENUM (
    'NOT_SET',
    'MINIMIZE',
    'MAXIMIZE'
);


ALTER TYPE public.studydirection OWNER TO postgres;

--
-- Name: trialintermediatevaluetype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.trialintermediatevaluetype AS ENUM (
    'FINITE',
    'INF_POS',
    'INF_NEG',
    'NAN'
);


ALTER TYPE public.trialintermediatevaluetype OWNER TO postgres;

--
-- Name: trialstate; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.trialstate AS ENUM (
    'RUNNING',
    'COMPLETE',
    'PRUNED',
    'FAIL',
    'WAITING'
);


ALTER TYPE public.trialstate OWNER TO postgres;

--
-- Name: trialvaluetype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.trialvaluetype AS ENUM (
    'FINITE',
    'INF_POS',
    'INF_NEG'
);


ALTER TYPE public.trialvaluetype OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: migrations; Type: TABLE; Schema: meta; Owner: postgres
--

CREATE TABLE meta.migrations (
    version text NOT NULL,
    name text,
    applied_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE meta.migrations OWNER TO postgres;

--
-- Name: dataset_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dataset_metadata (
    id bigint NOT NULL,
    dataset_id bigint NOT NULL,
    key text NOT NULL,
    value text,
    type text,
    extra_info json
);


ALTER TABLE public.dataset_metadata OWNER TO postgres;

--
-- Name: dataset_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.dataset_metadata ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.dataset_metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dataset_registrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dataset_registrations (
    id bigint NOT NULL,
    dataset_id bigint NOT NULL,
    registration_id bigint NOT NULL
);


ALTER TABLE public.dataset_registrations OWNER TO postgres;

--
-- Name: dataset_relations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dataset_relations (
    id bigint NOT NULL,
    parent_dataset_id bigint NOT NULL,
    child_dataset_id bigint NOT NULL,
    CONSTRAINT dataset_relations_no_self_reference CHECK ((parent_dataset_id <> child_dataset_id))
);


ALTER TABLE public.dataset_relations OWNER TO postgres;

--
-- Name: dataset_relations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.dataset_relations ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.dataset_relations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: datasetmeasurements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.dataset_registrations ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.datasetmeasurements_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: datasets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.datasets (
    id bigint NOT NULL,
    file_path text NOT NULL,
    description text,
    datasettype_id bigint NOT NULL
);


ALTER TABLE public.datasets OWNER TO postgres;

--
-- Name: datasets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.datasets ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.datasets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: datasettypes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.datasettypes (
    id bigint NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.datasettypes OWNER TO postgres;

--
-- Name: datasettypes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.datasettypes ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.datasettypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: experiment_datasets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experiment_datasets (
    id integer NOT NULL,
    experiment_id integer NOT NULL,
    dataset_id bigint NOT NULL
);


ALTER TABLE public.experiment_datasets OWNER TO postgres;

--
-- Name: experiment_datasets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.experiment_datasets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.experiment_datasets_id_seq OWNER TO postgres;

--
-- Name: experiment_datasets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.experiment_datasets_id_seq OWNED BY public.experiment_datasets.id;


--
-- Name: experiment_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experiment_metadata (
    id integer NOT NULL,
    experiment_id integer NOT NULL,
    key character varying(255) NOT NULL,
    value text,
    type character varying(100),
    extra_info jsonb
);


ALTER TABLE public.experiment_metadata OWNER TO postgres;

--
-- Name: experiment_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.experiment_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.experiment_metadata_id_seq OWNER TO postgres;

--
-- Name: experiment_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.experiment_metadata_id_seq OWNED BY public.experiment_metadata.id;


--
-- Name: experiments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experiments (
    id integer NOT NULL,
    folder_path text NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.experiments OWNER TO postgres;

--
-- Name: experiments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.experiments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.experiments_id_seq OWNER TO postgres;

--
-- Name: experiments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.experiments_id_seq OWNED BY public.experiments.id;


--
-- Name: fabrications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fabrications (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text
);


ALTER TABLE public.fabrications OWNER TO postgres;

--
-- Name: TABLE fabrications; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.fabrications IS 'Stores information about distinct fabrication processes or methods.';


--
-- Name: fabrication_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fabrication_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fabrication_id_seq OWNER TO postgres;

--
-- Name: fabrication_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fabrication_id_seq OWNED BY public.fabrications.id;


--
-- Name: fabrication_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fabrication_metadata (
    id integer NOT NULL,
    fabrication_id integer NOT NULL,
    key character varying(255) NOT NULL,
    value text NOT NULL,
    type character varying(100),
    extra_info jsonb
);


ALTER TABLE public.fabrication_metadata OWNER TO postgres;

--
-- Name: TABLE fabrication_metadata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.fabrication_metadata IS 'Stores flexible key-value metadata for each entry in the fabrication table.';


--
-- Name: fabrication_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fabrication_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fabrication_metadata_id_seq OWNER TO postgres;

--
-- Name: fabrication_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fabrication_metadata_id_seq OWNED BY public.fabrication_metadata.id;


--
-- Name: registrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registrations (
    id bigint NOT NULL,
    reference_measurement_id bigint NOT NULL,
    registered_measurement_id bigint NOT NULL,
    registration_matrix text NOT NULL,
    description text
);


ALTER TABLE public.registrations OWNER TO postgres;

--
-- Name: file_registrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.registrations ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.file_registrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: material_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.material_metadata (
    id bigint NOT NULL,
    material_id bigint NOT NULL,
    key text NOT NULL,
    value text NOT NULL,
    type text,
    extra_info json
);


ALTER TABLE public.material_metadata OWNER TO postgres;

--
-- Name: material_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.material_metadata ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.material_metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: materials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.materials (
    id bigint NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.materials OWNER TO postgres;

--
-- Name: materials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.materials ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.materials_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: measurements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.measurements (
    id bigint NOT NULL,
    file_path text NOT NULL,
    parent_measurement_id bigint,
    measurementtype_id bigint NOT NULL
);


ALTER TABLE public.measurements OWNER TO postgres;

--
-- Name: measurement_files_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.measurements ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.measurement_files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: measurement_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.measurement_metadata (
    id bigint NOT NULL,
    measurement_id bigint NOT NULL,
    key text NOT NULL,
    value text,
    type text,
    extra_info json
);


ALTER TABLE public.measurement_metadata OWNER TO postgres;

--
-- Name: measurement_files_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.measurement_metadata ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.measurement_files_metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: registration_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registration_metadata (
    id integer NOT NULL,
    registration_id integer NOT NULL,
    key character varying(255) NOT NULL,
    value text NOT NULL,
    type character varying(100),
    extra_info jsonb
);


ALTER TABLE public.registration_metadata OWNER TO postgres;

--
-- Name: TABLE registration_metadata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.registration_metadata IS 'Stores flexible key-value metadata for each entry in the measurement_registrations table.';


--
-- Name: measurement_registration_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.measurement_registration_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.measurement_registration_metadata_id_seq OWNER TO postgres;

--
-- Name: measurement_registration_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.measurement_registration_metadata_id_seq OWNED BY public.registration_metadata.id;


--
-- Name: measurementtype_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.measurementtype_metadata (
    id bigint NOT NULL,
    measurementtype_id bigint,
    key text NOT NULL,
    value text,
    type text,
    extra_info json
);


ALTER TABLE public.measurementtype_metadata OWNER TO postgres;

--
-- Name: measurement_type_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.measurementtype_metadata ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.measurement_type_metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: measurementtypes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.measurementtypes (
    id bigint NOT NULL,
    name text NOT NULL,
    description text
);


ALTER TABLE public.measurementtypes OWNER TO postgres;

--
-- Name: measurementtypes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.measurementtypes ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.measurementtypes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: onlypores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.onlypores (
    id bigint NOT NULL,
    measurement_id bigint NOT NULL,
    onlypores_path text NOT NULL,
    material_mask_path text NOT NULL,
    binary_path text NOT NULL
);


ALTER TABLE public.onlypores OWNER TO postgres;

--
-- Name: onlypores_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.onlypores ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.onlypores_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: onlypores_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.onlypores_metadata (
    id bigint NOT NULL,
    onlypores_id bigint NOT NULL,
    key text NOT NULL,
    value text,
    type text,
    extra_info json
);


ALTER TABLE public.onlypores_metadata OWNER TO postgres;

--
-- Name: onlypores_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.onlypores_metadata ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.onlypores_metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: panels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.panels (
    id bigint NOT NULL,
    name text NOT NULL,
    material_id bigint NOT NULL,
    description text,
    fabrication_id integer
);


ALTER TABLE public.panels OWNER TO postgres;

--
-- Name: COLUMN panels.fabrication_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.panels.fabrication_id IS 'Foreign key referencing the fabrication method used to create the panel.';


--
-- Name: panel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.panels ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.panel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: panel_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.panel_metadata (
    id bigint NOT NULL,
    panel_id bigint NOT NULL,
    key text NOT NULL,
    value text,
    type text,
    extra_info json
);


ALTER TABLE public.panel_metadata OWNER TO postgres;

--
-- Name: panel_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.panel_metadata ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.panel_metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: sample_measurements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sample_measurements (
    id bigint NOT NULL,
    sample_id bigint NOT NULL,
    measurement_id bigint NOT NULL
);


ALTER TABLE public.sample_measurements OWNER TO postgres;

--
-- Name: sample_measurements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.sample_measurements ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.sample_measurements_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: sample_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sample_metadata (
    id bigint NOT NULL,
    sample_id bigint NOT NULL,
    key text NOT NULL,
    value text,
    type text,
    extra_info json
);


ALTER TABLE public.sample_metadata OWNER TO postgres;

--
-- Name: sample_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.sample_metadata ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.sample_metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: samples; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.samples (
    id bigint NOT NULL,
    name text NOT NULL,
    description text,
    panel_id bigint NOT NULL
);


ALTER TABLE public.samples OWNER TO postgres;

--
-- Name: samples_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.samples ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.samples_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: experiment_datasets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_datasets ALTER COLUMN id SET DEFAULT nextval('public.experiment_datasets_id_seq'::regclass);


--
-- Name: experiment_metadata id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_metadata ALTER COLUMN id SET DEFAULT nextval('public.experiment_metadata_id_seq'::regclass);


--
-- Name: experiments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiments ALTER COLUMN id SET DEFAULT nextval('public.experiments_id_seq'::regclass);


--
-- Name: fabrication_metadata id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabrication_metadata ALTER COLUMN id SET DEFAULT nextval('public.fabrication_metadata_id_seq'::regclass);


--
-- Name: fabrications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabrications ALTER COLUMN id SET DEFAULT nextval('public.fabrication_id_seq'::regclass);


--
-- Name: registration_metadata id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration_metadata ALTER COLUMN id SET DEFAULT nextval('public.measurement_registration_metadata_id_seq'::regclass);


--
-- Name: migrations migrations_pkey; Type: CONSTRAINT; Schema: meta; Owner: postgres
--

ALTER TABLE ONLY meta.migrations
    ADD CONSTRAINT migrations_pkey PRIMARY KEY (version);


--
-- Name: dataset_metadata dataset_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataset_metadata
    ADD CONSTRAINT dataset_metadata_pkey PRIMARY KEY (id);


--
-- Name: dataset_relations dataset_relations_parent_child_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataset_relations
    ADD CONSTRAINT dataset_relations_parent_child_key UNIQUE (parent_dataset_id, child_dataset_id);


--
-- Name: dataset_relations dataset_relations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataset_relations
    ADD CONSTRAINT dataset_relations_pkey PRIMARY KEY (id);


--
-- Name: dataset_registrations datasetmeasurements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataset_registrations
    ADD CONSTRAINT datasetmeasurements_pkey PRIMARY KEY (id);


--
-- Name: datasets datasets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT datasets_pkey PRIMARY KEY (id);


--
-- Name: datasettypes datasettypes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.datasettypes
    ADD CONSTRAINT datasettypes_pkey PRIMARY KEY (id);


--
-- Name: experiment_datasets experiment_datasets_experiment_id_dataset_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_datasets
    ADD CONSTRAINT experiment_datasets_experiment_id_dataset_id_key UNIQUE (experiment_id, dataset_id);


--
-- Name: experiment_datasets experiment_datasets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_datasets
    ADD CONSTRAINT experiment_datasets_pkey PRIMARY KEY (id);


--
-- Name: experiment_metadata experiment_metadata_experiment_id_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_metadata
    ADD CONSTRAINT experiment_metadata_experiment_id_key_key UNIQUE (experiment_id, key);


--
-- Name: experiment_metadata experiment_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_metadata
    ADD CONSTRAINT experiment_metadata_pkey PRIMARY KEY (id);


--
-- Name: experiments experiments_folder_path_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_folder_path_key UNIQUE (folder_path);


--
-- Name: experiments experiments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_pkey PRIMARY KEY (id);


--
-- Name: fabrication_metadata fabrication_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabrication_metadata
    ADD CONSTRAINT fabrication_metadata_pkey PRIMARY KEY (id);


--
-- Name: fabrications fabrication_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabrications
    ADD CONSTRAINT fabrication_name_key UNIQUE (name);


--
-- Name: fabrications fabrication_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabrications
    ADD CONSTRAINT fabrication_pkey PRIMARY KEY (id);


--
-- Name: registrations file_registrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registrations
    ADD CONSTRAINT file_registrations_pkey PRIMARY KEY (id);


--
-- Name: material_metadata material_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_metadata
    ADD CONSTRAINT material_metadata_pkey PRIMARY KEY (id);


--
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (id);


--
-- Name: measurements measurement_files_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT measurement_files_pkey PRIMARY KEY (id);


--
-- Name: measurement_metadata measurement_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurement_metadata
    ADD CONSTRAINT measurement_metadata_pkey PRIMARY KEY (id);


--
-- Name: registration_metadata measurement_registration_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration_metadata
    ADD CONSTRAINT measurement_registration_metadata_pkey PRIMARY KEY (id);


--
-- Name: measurementtype_metadata measurement_type_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurementtype_metadata
    ADD CONSTRAINT measurement_type_metadata_pkey PRIMARY KEY (id);


--
-- Name: measurementtypes measurementtypes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurementtypes
    ADD CONSTRAINT measurementtypes_pkey PRIMARY KEY (id);


--
-- Name: onlypores_metadata onlypores_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.onlypores_metadata
    ADD CONSTRAINT onlypores_metadata_pkey PRIMARY KEY (id);


--
-- Name: onlypores onlypores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.onlypores
    ADD CONSTRAINT onlypores_pkey PRIMARY KEY (id);


--
-- Name: onlypores onlypores_unique_onlypores_path; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.onlypores
    ADD CONSTRAINT onlypores_unique_onlypores_path UNIQUE (onlypores_path);


--
-- Name: panel_metadata panel_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panel_metadata
    ADD CONSTRAINT panel_metadata_pkey PRIMARY KEY (id);


--
-- Name: panels panel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panels
    ADD CONSTRAINT panel_pkey PRIMARY KEY (id);


--
-- Name: sample_measurements sample_measurements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample_measurements
    ADD CONSTRAINT sample_measurements_pkey PRIMARY KEY (id);


--
-- Name: sample_metadata sample_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample_metadata
    ADD CONSTRAINT sample_metadata_pkey PRIMARY KEY (id);


--
-- Name: samples samples_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.samples
    ADD CONSTRAINT samples_pkey PRIMARY KEY (id);


--
-- Name: datasets unique_datasets_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT unique_datasets_name UNIQUE (file_path);


--
-- Name: datasettypes unique_datasettype_description; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.datasettypes
    ADD CONSTRAINT unique_datasettype_description UNIQUE (description);


--
-- Name: measurements unique_file_path; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT unique_file_path UNIQUE (file_path);


--
-- Name: materials unique_materials_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT unique_materials_name UNIQUE (name);


--
-- Name: measurementtypes unique_measurementtypes_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurementtypes
    ADD CONSTRAINT unique_measurementtypes_name UNIQUE (name);


--
-- Name: panels unique_panels_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panels
    ADD CONSTRAINT unique_panels_name UNIQUE (name);


--
-- Name: samples unique_samples_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.samples
    ADD CONSTRAINT unique_samples_name UNIQUE (name);


--
-- Name: fki_dataset_metadata_dataset_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_dataset_metadata_dataset_id_fkey ON public.dataset_metadata USING btree (dataset_id);


--
-- Name: fki_datasetmeasurements_dataset_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_datasetmeasurements_dataset_id_fkey ON public.dataset_registrations USING btree (dataset_id);


--
-- Name: fki_datasetmeasurements_measurement_file_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_datasetmeasurements_measurement_file_id_fkey ON public.dataset_registrations USING btree (registration_id);


--
-- Name: fki_file_registrations_reference_file_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_file_registrations_reference_file_id_fkey ON public.registrations USING btree (reference_measurement_id);


--
-- Name: fki_file_registrations_registered_file_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_file_registrations_registered_file_id_fkey ON public.registrations USING btree (registered_measurement_id);


--
-- Name: fki_material_metadata_material_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_material_metadata_material_id_fkey ON public.material_metadata USING btree (material_id);


--
-- Name: fki_measurement_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_measurement_fkey ON public.sample_measurements USING btree (measurement_id);


--
-- Name: fki_measurement_metadata_measurement_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_measurement_metadata_measurement_id_fkey ON public.measurement_metadata USING btree (measurement_id);


--
-- Name: fki_measurement_type_metadata_measurement_type_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_measurement_type_metadata_measurement_type_id_fkey ON public.measurementtype_metadata USING btree (measurementtype_id);


--
-- Name: fki_panel_metadata_panel_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_panel_metadata_panel_id_fkey ON public.panel_metadata USING btree (panel_id);


--
-- Name: fki_sample_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_sample_fkey ON public.sample_measurements USING btree (sample_id);


--
-- Name: fki_sample_metadata_sample_id_fkey; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_sample_metadata_sample_id_fkey ON public.sample_metadata USING btree (sample_id);


--
-- Name: onlypores_measurement_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX onlypores_measurement_id_idx ON public.onlypores USING btree (measurement_id);


--
-- Name: onlypores_metadata_onlypores_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX onlypores_metadata_onlypores_id_idx ON public.onlypores_metadata USING btree (onlypores_id);


--
-- Name: dataset_metadata dataset_metadata_dataset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataset_metadata
    ADD CONSTRAINT dataset_metadata_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id) ON DELETE CASCADE;


--
-- Name: dataset_relations dataset_relations_child_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataset_relations
    ADD CONSTRAINT dataset_relations_child_fkey FOREIGN KEY (child_dataset_id) REFERENCES public.datasets(id) ON DELETE CASCADE;


--
-- Name: dataset_relations dataset_relations_parent_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataset_relations
    ADD CONSTRAINT dataset_relations_parent_fkey FOREIGN KEY (parent_dataset_id) REFERENCES public.datasets(id) ON DELETE CASCADE;


--
-- Name: dataset_registrations datasetregistrations_dataset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataset_registrations
    ADD CONSTRAINT datasetregistrations_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id) ON DELETE CASCADE;


--
-- Name: dataset_registrations datasetregistrations_registration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dataset_registrations
    ADD CONSTRAINT datasetregistrations_registration_id_fkey FOREIGN KEY (registration_id) REFERENCES public.registrations(id) ON DELETE CASCADE NOT VALID;


--
-- Name: datasets datasets_datasettype_foreign_key; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.datasets
    ADD CONSTRAINT datasets_datasettype_foreign_key FOREIGN KEY (datasettype_id) REFERENCES public.datasettypes(id) NOT VALID;


--
-- Name: experiment_datasets experiment_datasets_dataset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_datasets
    ADD CONSTRAINT experiment_datasets_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES public.datasets(id) ON DELETE CASCADE;


--
-- Name: experiment_datasets experiment_datasets_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_datasets
    ADD CONSTRAINT experiment_datasets_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.experiments(id) ON DELETE CASCADE;


--
-- Name: experiment_metadata experiment_metadata_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_metadata
    ADD CONSTRAINT experiment_metadata_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.experiments(id) ON DELETE CASCADE;


--
-- Name: fabrication_metadata fabrication_metadata_fabrication_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fabrication_metadata
    ADD CONSTRAINT fabrication_metadata_fabrication_id_fkey FOREIGN KEY (fabrication_id) REFERENCES public.fabrications(id) ON DELETE CASCADE;


--
-- Name: registrations file_registrations_reference_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registrations
    ADD CONSTRAINT file_registrations_reference_file_id_fkey FOREIGN KEY (reference_measurement_id) REFERENCES public.measurements(id) ON DELETE CASCADE;


--
-- Name: registrations file_registrations_registered_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registrations
    ADD CONSTRAINT file_registrations_registered_file_id_fkey FOREIGN KEY (registered_measurement_id) REFERENCES public.measurements(id) ON DELETE CASCADE;


--
-- Name: material_metadata material_metadata_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.material_metadata
    ADD CONSTRAINT material_metadata_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id) ON DELETE CASCADE;


--
-- Name: measurements measurement_files_measurementtype_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT measurement_files_measurementtype_id_fkey FOREIGN KEY (measurementtype_id) REFERENCES public.measurementtypes(id);


--
-- Name: measurements measurement_files_parent_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT measurement_files_parent_file_id_fkey FOREIGN KEY (parent_measurement_id) REFERENCES public.measurements(id);


--
-- Name: measurement_metadata measurement_metadata_measurement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurement_metadata
    ADD CONSTRAINT measurement_metadata_measurement_id_fkey FOREIGN KEY (measurement_id) REFERENCES public.measurements(id) ON DELETE CASCADE;


--
-- Name: registration_metadata measurement_registration_metad_measurement_registration_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration_metadata
    ADD CONSTRAINT measurement_registration_metad_measurement_registration_id_fkey FOREIGN KEY (registration_id) REFERENCES public.registrations(id) ON DELETE CASCADE;


--
-- Name: measurementtype_metadata measurement_type_metadata_measurement_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurementtype_metadata
    ADD CONSTRAINT measurement_type_metadata_measurement_type_id_fkey FOREIGN KEY (measurementtype_id) REFERENCES public.measurementtypes(id) ON DELETE CASCADE;


--
-- Name: onlypores onlypores_measurement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.onlypores
    ADD CONSTRAINT onlypores_measurement_id_fkey FOREIGN KEY (measurement_id) REFERENCES public.measurements(id) ON DELETE CASCADE;


--
-- Name: onlypores_metadata onlypores_metadata_onlypores_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.onlypores_metadata
    ADD CONSTRAINT onlypores_metadata_onlypores_id_fkey FOREIGN KEY (onlypores_id) REFERENCES public.onlypores(id) ON DELETE CASCADE;


--
-- Name: panels panel_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panels
    ADD CONSTRAINT panel_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id);


--
-- Name: panel_metadata panel_metadata_panel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panel_metadata
    ADD CONSTRAINT panel_metadata_panel_id_fkey FOREIGN KEY (panel_id) REFERENCES public.panels(id) ON DELETE CASCADE;


--
-- Name: panels panels_fabrication_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.panels
    ADD CONSTRAINT panels_fabrication_id_fkey FOREIGN KEY (fabrication_id) REFERENCES public.fabrications(id);


--
-- Name: sample_measurements sample_measurements_measurement_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample_measurements
    ADD CONSTRAINT sample_measurements_measurement_fkey FOREIGN KEY (measurement_id) REFERENCES public.measurements(id) ON DELETE CASCADE;


--
-- Name: sample_measurements sample_measurements_sample_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample_measurements
    ADD CONSTRAINT sample_measurements_sample_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(id) ON DELETE CASCADE;


--
-- Name: sample_metadata sample_metadata_sample_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sample_metadata
    ADD CONSTRAINT sample_metadata_sample_id_fkey FOREIGN KEY (sample_id) REFERENCES public.samples(id) ON DELETE CASCADE;


--
-- Name: samples samples_panel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.samples
    ADD CONSTRAINT samples_panel_id_fkey FOREIGN KEY (panel_id) REFERENCES public.panels(id);


--
-- Name: SCHEMA meta; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA meta TO diego;
GRANT USAGE ON SCHEMA meta TO miguel;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO "jorge.cabrejas";
GRANT USAGE ON SCHEMA public TO claude;
GRANT USAGE ON SCHEMA public TO diego;
GRANT USAGE ON SCHEMA public TO miguel;


--
-- Name: TABLE migrations; Type: ACL; Schema: meta; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE meta.migrations TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE meta.migrations TO miguel;


--
-- Name: TABLE dataset_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.dataset_metadata TO "jorge.cabrejas";
GRANT ALL ON TABLE public.dataset_metadata TO "alberto.vicente";
GRANT SELECT ON TABLE public.dataset_metadata TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.dataset_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.dataset_metadata TO miguel;


--
-- Name: SEQUENCE dataset_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.dataset_metadata_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.dataset_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.dataset_metadata_id_seq TO miguel;


--
-- Name: TABLE dataset_registrations; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.dataset_registrations TO "jorge.cabrejas";
GRANT ALL ON TABLE public.dataset_registrations TO "alberto.vicente";
GRANT SELECT ON TABLE public.dataset_registrations TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.dataset_registrations TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.dataset_registrations TO miguel;


--
-- Name: TABLE dataset_relations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.dataset_relations TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.dataset_relations TO miguel;


--
-- Name: SEQUENCE dataset_relations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.dataset_relations_id_seq TO diego;
GRANT ALL ON SEQUENCE public.dataset_relations_id_seq TO miguel;


--
-- Name: SEQUENCE datasetmeasurements_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.datasetmeasurements_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.datasetmeasurements_id_seq TO diego;
GRANT ALL ON SEQUENCE public.datasetmeasurements_id_seq TO miguel;


--
-- Name: TABLE datasets; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.datasets TO "jorge.cabrejas";
GRANT ALL ON TABLE public.datasets TO "alberto.vicente";
GRANT SELECT ON TABLE public.datasets TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.datasets TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.datasets TO miguel;


--
-- Name: SEQUENCE datasets_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.datasets_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.datasets_id_seq TO diego;
GRANT ALL ON SEQUENCE public.datasets_id_seq TO miguel;


--
-- Name: TABLE datasettypes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.datasettypes TO "jorge.cabrejas";
GRANT ALL ON TABLE public.datasettypes TO "alberto.vicente";
GRANT SELECT ON TABLE public.datasettypes TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.datasettypes TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.datasettypes TO miguel;


--
-- Name: SEQUENCE datasettypes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.datasettypes_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.datasettypes_id_seq TO diego;
GRANT ALL ON SEQUENCE public.datasettypes_id_seq TO miguel;


--
-- Name: TABLE experiment_datasets; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.experiment_datasets TO "jorge.cabrejas";
GRANT ALL ON TABLE public.experiment_datasets TO "alberto.vicente";
GRANT SELECT ON TABLE public.experiment_datasets TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.experiment_datasets TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.experiment_datasets TO miguel;


--
-- Name: SEQUENCE experiment_datasets_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.experiment_datasets_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.experiment_datasets_id_seq TO diego;
GRANT ALL ON SEQUENCE public.experiment_datasets_id_seq TO miguel;


--
-- Name: TABLE experiment_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.experiment_metadata TO "jorge.cabrejas";
GRANT ALL ON TABLE public.experiment_metadata TO "alberto.vicente";
GRANT SELECT ON TABLE public.experiment_metadata TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.experiment_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.experiment_metadata TO miguel;


--
-- Name: SEQUENCE experiment_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.experiment_metadata_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.experiment_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.experiment_metadata_id_seq TO miguel;


--
-- Name: TABLE experiments; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.experiments TO "jorge.cabrejas";
GRANT ALL ON TABLE public.experiments TO "alberto.vicente";
GRANT SELECT ON TABLE public.experiments TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.experiments TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.experiments TO miguel;


--
-- Name: SEQUENCE experiments_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.experiments_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.experiments_id_seq TO diego;
GRANT ALL ON SEQUENCE public.experiments_id_seq TO miguel;


--
-- Name: TABLE fabrications; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.fabrications TO "jorge.cabrejas";
GRANT ALL ON TABLE public.fabrications TO "alberto.vicente";
GRANT SELECT ON TABLE public.fabrications TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.fabrications TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.fabrications TO miguel;


--
-- Name: SEQUENCE fabrication_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.fabrication_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.fabrication_id_seq TO diego;
GRANT ALL ON SEQUENCE public.fabrication_id_seq TO miguel;


--
-- Name: TABLE fabrication_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.fabrication_metadata TO "jorge.cabrejas";
GRANT ALL ON TABLE public.fabrication_metadata TO "alberto.vicente";
GRANT SELECT ON TABLE public.fabrication_metadata TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.fabrication_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.fabrication_metadata TO miguel;


--
-- Name: SEQUENCE fabrication_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.fabrication_metadata_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.fabrication_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.fabrication_metadata_id_seq TO miguel;


--
-- Name: TABLE registrations; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.registrations TO "jorge.cabrejas";
GRANT ALL ON TABLE public.registrations TO "alberto.vicente";
GRANT SELECT ON TABLE public.registrations TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.registrations TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.registrations TO miguel;


--
-- Name: SEQUENCE file_registrations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.file_registrations_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.file_registrations_id_seq TO diego;
GRANT ALL ON SEQUENCE public.file_registrations_id_seq TO miguel;


--
-- Name: TABLE material_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.material_metadata TO "jorge.cabrejas";
GRANT ALL ON TABLE public.material_metadata TO "alberto.vicente";
GRANT SELECT ON TABLE public.material_metadata TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.material_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.material_metadata TO miguel;


--
-- Name: SEQUENCE material_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.material_metadata_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.material_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.material_metadata_id_seq TO miguel;


--
-- Name: TABLE materials; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.materials TO "jorge.cabrejas";
GRANT ALL ON TABLE public.materials TO "alberto.vicente";
GRANT SELECT ON TABLE public.materials TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.materials TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.materials TO miguel;


--
-- Name: SEQUENCE materials_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.materials_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.materials_id_seq TO diego;
GRANT ALL ON SEQUENCE public.materials_id_seq TO miguel;


--
-- Name: TABLE measurements; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.measurements TO "jorge.cabrejas";
GRANT ALL ON TABLE public.measurements TO "alberto.vicente";
GRANT SELECT ON TABLE public.measurements TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.measurements TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.measurements TO miguel;


--
-- Name: SEQUENCE measurement_files_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.measurement_files_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.measurement_files_id_seq TO diego;
GRANT ALL ON SEQUENCE public.measurement_files_id_seq TO miguel;


--
-- Name: TABLE measurement_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.measurement_metadata TO "jorge.cabrejas";
GRANT ALL ON TABLE public.measurement_metadata TO "alberto.vicente";
GRANT SELECT ON TABLE public.measurement_metadata TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.measurement_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.measurement_metadata TO miguel;


--
-- Name: SEQUENCE measurement_files_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.measurement_files_metadata_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.measurement_files_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.measurement_files_metadata_id_seq TO miguel;


--
-- Name: TABLE registration_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.registration_metadata TO "jorge.cabrejas";
GRANT ALL ON TABLE public.registration_metadata TO "alberto.vicente";
GRANT SELECT ON TABLE public.registration_metadata TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.registration_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.registration_metadata TO miguel;


--
-- Name: SEQUENCE measurement_registration_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.measurement_registration_metadata_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.measurement_registration_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.measurement_registration_metadata_id_seq TO miguel;


--
-- Name: TABLE measurementtype_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.measurementtype_metadata TO "jorge.cabrejas";
GRANT ALL ON TABLE public.measurementtype_metadata TO "alberto.vicente";
GRANT SELECT ON TABLE public.measurementtype_metadata TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.measurementtype_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.measurementtype_metadata TO miguel;


--
-- Name: SEQUENCE measurement_type_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.measurement_type_metadata_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.measurement_type_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.measurement_type_metadata_id_seq TO miguel;


--
-- Name: TABLE measurementtypes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.measurementtypes TO "jorge.cabrejas";
GRANT ALL ON TABLE public.measurementtypes TO "alberto.vicente";
GRANT SELECT ON TABLE public.measurementtypes TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.measurementtypes TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.measurementtypes TO miguel;


--
-- Name: SEQUENCE measurementtypes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.measurementtypes_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.measurementtypes_id_seq TO diego;
GRANT ALL ON SEQUENCE public.measurementtypes_id_seq TO miguel;


--
-- Name: TABLE onlypores; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.onlypores TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.onlypores TO miguel;


--
-- Name: SEQUENCE onlypores_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.onlypores_id_seq TO diego;
GRANT ALL ON SEQUENCE public.onlypores_id_seq TO miguel;


--
-- Name: TABLE onlypores_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.onlypores_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.onlypores_metadata TO miguel;


--
-- Name: SEQUENCE onlypores_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.onlypores_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.onlypores_metadata_id_seq TO miguel;


--
-- Name: TABLE panels; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.panels TO "jorge.cabrejas";
GRANT ALL ON TABLE public.panels TO "alberto.vicente";
GRANT SELECT ON TABLE public.panels TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.panels TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.panels TO miguel;


--
-- Name: SEQUENCE panel_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.panel_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.panel_id_seq TO diego;
GRANT ALL ON SEQUENCE public.panel_id_seq TO miguel;


--
-- Name: TABLE panel_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.panel_metadata TO "jorge.cabrejas";
GRANT ALL ON TABLE public.panel_metadata TO "alberto.vicente";
GRANT SELECT ON TABLE public.panel_metadata TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.panel_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.panel_metadata TO miguel;


--
-- Name: SEQUENCE panel_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.panel_metadata_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.panel_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.panel_metadata_id_seq TO miguel;


--
-- Name: TABLE sample_measurements; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sample_measurements TO "jorge.cabrejas";
GRANT ALL ON TABLE public.sample_measurements TO "alberto.vicente";
GRANT SELECT ON TABLE public.sample_measurements TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sample_measurements TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sample_measurements TO miguel;


--
-- Name: SEQUENCE sample_measurements_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.sample_measurements_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.sample_measurements_id_seq TO diego;
GRANT ALL ON SEQUENCE public.sample_measurements_id_seq TO miguel;


--
-- Name: TABLE sample_metadata; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sample_metadata TO "jorge.cabrejas";
GRANT ALL ON TABLE public.sample_metadata TO "alberto.vicente";
GRANT SELECT ON TABLE public.sample_metadata TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sample_metadata TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.sample_metadata TO miguel;


--
-- Name: SEQUENCE sample_metadata_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.sample_metadata_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.sample_metadata_id_seq TO diego;
GRANT ALL ON SEQUENCE public.sample_metadata_id_seq TO miguel;


--
-- Name: TABLE samples; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.samples TO "jorge.cabrejas";
GRANT ALL ON TABLE public.samples TO "alberto.vicente";
GRANT SELECT ON TABLE public.samples TO claude;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.samples TO diego;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.samples TO miguel;


--
-- Name: SEQUENCE samples_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.samples_id_seq TO "alberto.vicente";
GRANT ALL ON SEQUENCE public.samples_id_seq TO diego;
GRANT ALL ON SEQUENCE public.samples_id_seq TO miguel;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: meta; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA meta GRANT ALL ON SEQUENCES TO diego;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA meta GRANT ALL ON SEQUENCES TO miguel;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: meta; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA meta GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO diego;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA meta GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO miguel;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO diego;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO miguel;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: alberto.vicente
--

ALTER DEFAULT PRIVILEGES FOR ROLE "alberto.vicente" IN SCHEMA public GRANT SELECT ON TABLES TO claude;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO diego;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO miguel;


--
-- PostgreSQL database dump complete
--

\unrestrict GKAu0OOg2fgEA0zY9yvdbRZYZLR91o6rlY6YQzpkNBVhWEDjPPJ16QhIZfSoW8E

