--
-- PostgreSQL database dump
--

\restrict hfflf29O8KgnDhUR0vxF3igMXRWNyBuQ81E6hDcqnJ7cALRDfKPwZYmd44fc5Bt

-- Dumped from database version 18.3 (Debian 18.3-1.pgdg13+1)
-- Dumped by pg_dump version 18.3 (Debian 18.3-1.pgdg13+1)

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
-- Name: actualizar_updated_at(); Type: FUNCTION; Schema: public; Owner: crm_admin
--

CREATE FUNCTION public.actualizar_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = current_timestamp;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.actualizar_updated_at() OWNER TO crm_admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: administradorcondominio; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.administradorcondominio (
    id integer NOT NULL,
    nombre_administrador text NOT NULL,
    nombre_contacto text,
    telefono text,
    correo text
);


ALTER TABLE public.administradorcondominio OWNER TO crm_admin;

--
-- Name: administradorcondominio_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.administradorcondominio_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.administradorcondominio_id_seq OWNER TO crm_admin;

--
-- Name: administradorcondominio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.administradorcondominio_id_seq OWNED BY public.administradorcondominio.id;


--
-- Name: cierremensual; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.cierremensual (
    id integer NOT NULL,
    year integer NOT NULL,
    mes integer NOT NULL,
    fecha_cierre timestamp with time zone NOT NULL,
    valor_uf_cierre real NOT NULL,
    cerrado_por character varying(10) NOT NULL
);


ALTER TABLE public.cierremensual OWNER TO crm_admin;

--
-- Name: cierremensual_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.cierremensual_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cierremensual_id_seq OWNER TO crm_admin;

--
-- Name: cierremensual_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.cierremensual_id_seq OWNED BY public.cierremensual.id;


--
-- Name: cliente; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.cliente (
    id integer NOT NULL,
    id_prospecto integer NOT NULL,
    rut_ej_renovacion_asignado character varying(10),
    rut_as_renovacion_asignado character varying(10),
    rut_ej_cobranza_asignado character varying(10)
);


ALTER TABLE public.cliente OWNER TO crm_admin;

--
-- Name: cliente_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.cliente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cliente_id_seq OWNER TO crm_admin;

--
-- Name: cliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.cliente_id_seq OWNED BY public.cliente.id;


--
-- Name: coberturariesgo; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.coberturariesgo (
    id integer NOT NULL,
    id_cobertura_tipo_riesgo integer NOT NULL,
    nombre text NOT NULL
);


ALTER TABLE public.coberturariesgo OWNER TO crm_admin;

--
-- Name: coberturariesgo_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.coberturariesgo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.coberturariesgo_id_seq OWNER TO crm_admin;

--
-- Name: coberturariesgo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.coberturariesgo_id_seq OWNED BY public.coberturariesgo.id;


--
-- Name: coberturatiporiesgo; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.coberturatiporiesgo (
    id integer NOT NULL,
    nombre text NOT NULL
);


ALTER TABLE public.coberturatiporiesgo OWNER TO crm_admin;

--
-- Name: coberturatiporiesgo_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.coberturatiporiesgo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.coberturatiporiesgo_id_seq OWNER TO crm_admin;

--
-- Name: coberturatiporiesgo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.coberturatiporiesgo_id_seq OWNED BY public.coberturatiporiesgo.id;


--
-- Name: companiessugeridas; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.companiessugeridas (
    id_prospecto integer NOT NULL,
    id_company integer NOT NULL
);


ALTER TABLE public.companiessugeridas OWNER TO crm_admin;

--
-- Name: companycoberturariesgo; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.companycoberturariesgo (
    id_company_seguro integer NOT NULL,
    id_cobertura_riesgo integer NOT NULL,
    descripcion text NOT NULL
);


ALTER TABLE public.companycoberturariesgo OWNER TO crm_admin;

--
-- Name: companyseguros; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.companyseguros (
    id integer NOT NULL,
    nombre text NOT NULL
);


ALTER TABLE public.companyseguros OWNER TO crm_admin;

--
-- Name: companyseguros_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.companyseguros_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companyseguros_id_seq OWNER TO crm_admin;

--
-- Name: companyseguros_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.companyseguros_id_seq OWNED BY public.companyseguros.id;


--
-- Name: comunicadogerencia; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.comunicadogerencia (
    id integer NOT NULL,
    rut_gerente character varying(10) NOT NULL,
    titulo text NOT NULL,
    descripcion text NOT NULL,
    prioridad text,
    fecha timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    caducidad timestamp with time zone NOT NULL
);


ALTER TABLE public.comunicadogerencia OWNER TO crm_admin;

--
-- Name: comunicadogerencia_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.comunicadogerencia_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comunicadogerencia_id_seq OWNER TO crm_admin;

--
-- Name: comunicadogerencia_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.comunicadogerencia_id_seq OWNED BY public.comunicadogerencia.id;


--
-- Name: cotizacion; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.cotizacion (
    id integer NOT NULL,
    id_company integer NOT NULL,
    fecha_emision timestamp with time zone NOT NULL,
    fecha_vencimiento timestamp with time zone NOT NULL,
    monto_total_asegurado real NOT NULL,
    prima_adicional_asistencia real NOT NULL,
    tasa_afecta real NOT NULL,
    tasa_excenta real NOT NULL,
    tasa_politica real NOT NULL,
    id_solicitud integer NOT NULL,
    nombre_archivo text
);


ALTER TABLE public.cotizacion OWNER TO crm_admin;

--
-- Name: cotizacion_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.cotizacion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cotizacion_id_seq OWNER TO crm_admin;

--
-- Name: cotizacion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.cotizacion_id_seq OWNED BY public.cotizacion.id;


--
-- Name: cuota; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.cuota (
    id integer NOT NULL,
    id_plan_pago integer NOT NULL,
    numero_cuota integer NOT NULL,
    fecha_vencimiento timestamp with time zone NOT NULL,
    pagado boolean DEFAULT false NOT NULL,
    fecha_pago timestamp with time zone
);


ALTER TABLE public.cuota OWNER TO crm_admin;

--
-- Name: cuota_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.cuota_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cuota_id_seq OWNER TO crm_admin;

--
-- Name: cuota_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.cuota_id_seq OWNED BY public.cuota.id;


--
-- Name: detallecierremensual; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.detallecierremensual (
    id_cierre_mensual integer NOT NULL,
    rut_ejecutivo character varying(10) NOT NULL,
    numero_poliza text NOT NULL,
    comision_corredora_uf real NOT NULL,
    pct_comision_ejecutivo real NOT NULL,
    comision_uf real NOT NULL,
    comision_pesos real NOT NULL
);


ALTER TABLE public.detallecierremensual OWNER TO crm_admin;

--
-- Name: estadoinformativoprocesocomercial; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.estadoinformativoprocesocomercial (
    codigo text NOT NULL,
    codigo_etapa text NOT NULL,
    nombre text NOT NULL
);


ALTER TABLE public.estadoinformativoprocesocomercial OWNER TO crm_admin;

--
-- Name: estudiocomercialcondominio; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.estudiocomercialcondominio (
    id integer NOT NULL,
    id_solicitud integer NOT NULL,
    nombre_archivo text NOT NULL
);


ALTER TABLE public.estudiocomercialcondominio OWNER TO crm_admin;

--
-- Name: estudiocomercialcondominio_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.estudiocomercialcondominio_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estudiocomercialcondominio_id_seq OWNER TO crm_admin;

--
-- Name: estudiocomercialcondominio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.estudiocomercialcondominio_id_seq OWNED BY public.estudiocomercialcondominio.id;


--
-- Name: etapaprocesocomercial; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.etapaprocesocomercial (
    codigo text NOT NULL,
    nombre text NOT NULL,
    codigo_siguiente_etapa text,
    dias_limite integer,
    es_terminal boolean NOT NULL
);


ALTER TABLE public.etapaprocesocomercial OWNER TO crm_admin;

--
-- Name: etapaprocesocomercialparticular; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.etapaprocesocomercialparticular (
    id integer NOT NULL,
    id_proceso_comercial integer NOT NULL,
    codigo_etapa text NOT NULL,
    dias_limite_particular integer NOT NULL
);


ALTER TABLE public.etapaprocesocomercialparticular OWNER TO crm_admin;

--
-- Name: etapaprocesocomercialparticular_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.etapaprocesocomercialparticular_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.etapaprocesocomercialparticular_id_seq OWNER TO crm_admin;

--
-- Name: etapaprocesocomercialparticular_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.etapaprocesocomercialparticular_id_seq OWNED BY public.etapaprocesocomercialparticular.id;


--
-- Name: factorcuotascompany; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.factorcuotascompany (
    id_company integer NOT NULL,
    numero_cuotas integer NOT NULL,
    factor real NOT NULL
);


ALTER TABLE public.factorcuotascompany OWNER TO crm_admin;

--
-- Name: gestioncomercial; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.gestioncomercial (
    id integer NOT NULL,
    tipo character varying(15) NOT NULL,
    rut_usuario character varying(10) NOT NULL,
    id_prospecto integer NOT NULL,
    titulo text NOT NULL,
    estado_contacto text,
    observacion text,
    created_at timestamp with time zone NOT NULL,
    fecha_gestion timestamp with time zone NOT NULL
);


ALTER TABLE public.gestioncomercial OWNER TO crm_admin;

--
-- Name: gestioncomercial_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.gestioncomercial_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gestioncomercial_id_seq OWNER TO crm_admin;

--
-- Name: gestioncomercial_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.gestioncomercial_id_seq OWNED BY public.gestioncomercial.id;


--
-- Name: historialestadoinformativoprocesocomercial; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.historialestadoinformativoprocesocomercial (
    id integer NOT NULL,
    id_proceso_comercial integer CONSTRAINT historialestadoinformativoproceso_id_proceso_comercial_not_null NOT NULL,
    codigo_estado text CONSTRAINT historialestadoinformativoprocesocomerci_codigo_estado_not_null NOT NULL,
    fecha_registro timestamp with time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT historialestadoinformativoprocesocomerc_fecha_registro_not_null NOT NULL,
    observacion text,
    rut_registrado_por character varying(10) CONSTRAINT historialestadoinformativoprocesoco_rut_registrado_por_not_null NOT NULL
);


ALTER TABLE public.historialestadoinformativoprocesocomercial OWNER TO crm_admin;

--
-- Name: historialestadoinformativoprocesocomercial_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.historialestadoinformativoprocesocomercial_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historialestadoinformativoprocesocomercial_id_seq OWNER TO crm_admin;

--
-- Name: historialestadoinformativoprocesocomercial_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.historialestadoinformativoprocesocomercial_id_seq OWNED BY public.historialestadoinformativoprocesocomercial.id;


--
-- Name: lineanegocio; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.lineanegocio (
    id integer NOT NULL,
    nombre text NOT NULL,
    codigo character varying(20) NOT NULL
);


ALTER TABLE public.lineanegocio OWNER TO crm_admin;

--
-- Name: lineanegocio_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.lineanegocio_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lineanegocio_id_seq OWNER TO crm_admin;

--
-- Name: lineanegocio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.lineanegocio_id_seq OWNED BY public.lineanegocio.id;


--
-- Name: permiso; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.permiso (
    codigo text NOT NULL,
    descripcion text NOT NULL
);


ALTER TABLE public.permiso OWNER TO crm_admin;

--
-- Name: permisorol; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.permisorol (
    codigo_rol text NOT NULL,
    codigo_permiso text NOT NULL
);


ALTER TABLE public.permisorol OWNER TO crm_admin;

--
-- Name: planificacionprospecto; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.planificacionprospecto (
    id_prospecto integer NOT NULL,
    id_company integer,
    prima_vigente real NOT NULL,
    termino_vigencia timestamp with time zone,
    monto_asegurado_vigente real,
    fecha_envio_cotizacion timestamp with time zone
);


ALTER TABLE public.planificacionprospecto OWNER TO crm_admin;

--
-- Name: planpago; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.planpago (
    id integer NOT NULL,
    numero_poliza text NOT NULL
);


ALTER TABLE public.planpago OWNER TO crm_admin;

--
-- Name: planpago_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.planpago_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.planpago_id_seq OWNER TO crm_admin;

--
-- Name: planpago_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.planpago_id_seq OWNED BY public.planpago.id;


--
-- Name: poliza; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.poliza (
    numero_poliza text NOT NULL,
    id_cliente integer NOT NULL,
    prima_neta real NOT NULL,
    comision_corredora_pct real NOT NULL,
    fecha_emision timestamp with time zone,
    inicio_vigencia timestamp with time zone,
    fin_vigencia timestamp with time zone,
    id_company integer,
    id_proceso_comercial integer NOT NULL,
    cancelada boolean DEFAULT false NOT NULL,
    renovacion_cotizada boolean DEFAULT false NOT NULL,
    tipo character varying(15) NOT NULL
);


ALTER TABLE public.poliza OWNER TO crm_admin;

--
-- Name: procesocomercial; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.procesocomercial (
    id integer NOT NULL,
    id_prospecto integer NOT NULL,
    rut_ej_comercial character varying(10),
    id_producto integer NOT NULL,
    cerrado boolean DEFAULT false NOT NULL,
    codigo_estado_actual text,
    renovacion boolean NOT NULL,
    rut_ej_renovacion character varying(10),
    rut_as_renovacion character varying(10),
    motivo_cierre text,
    monto_asegurado_actual real,
    rut_ej_evaluacion character varying(10)
);


ALTER TABLE public.procesocomercial OWNER TO crm_admin;

--
-- Name: procesocomercial_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.procesocomercial_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.procesocomercial_id_seq OWNER TO crm_admin;

--
-- Name: procesocomercial_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.procesocomercial_id_seq OWNED BY public.procesocomercial.id;


--
-- Name: producto; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.producto (
    id integer NOT NULL,
    nombre text NOT NULL,
    id_linea_negocio integer NOT NULL,
    codigo text
);


ALTER TABLE public.producto OWNER TO crm_admin;

--
-- Name: producto_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.producto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.producto_id_seq OWNER TO crm_admin;

--
-- Name: producto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.producto_id_seq OWNED BY public.producto.id;


--
-- Name: prospecto; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.prospecto (
    id integer NOT NULL,
    rut_riesgo text,
    nombre_riesgo text,
    telefono_contacto text,
    correo_contacto text,
    direccion text,
    observaciones text,
    id_linea_negocio integer NOT NULL,
    rut_registrado_por character varying(10) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    region text,
    comuna text,
    rut_ej_comercial_asignado character varying(10),
    informacion_completa boolean,
    rut_ej_evaluacion_asignado character varying(10)
);


ALTER TABLE public.prospecto OWNER TO crm_admin;

--
-- Name: prospecto_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.prospecto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prospecto_id_seq OWNER TO crm_admin;

--
-- Name: prospecto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.prospecto_id_seq OWNED BY public.prospecto.id;


--
-- Name: prospectocondominio; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.prospectocondominio (
    id integer NOT NULL,
    tiene_locales_comerciales boolean,
    uso_del_condominio text,
    numero_pisos integer,
    numero_torres integer,
    cantidad_departamentos integer,
    cantidad_subterraneos integer,
    tiene_piscina boolean,
    year_construccion integer,
    metros_cuadrados real,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id_administrador integer,
    materialidad text,
    clasificacion_preliminar_incendio text,
    procesos_productivos boolean,
    ubicacion_piscina text,
    tiene_alarma_incendio boolean,
    tiene_sprinklers boolean,
    uf_por_metro_cuadrado real,
    porcentaje_depreciacion real,
    porcentaje_espacios_comunes real,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.prospectocondominio OWNER TO crm_admin;

--
-- Name: recordatorio; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.recordatorio (
    id integer NOT NULL,
    titulo text NOT NULL,
    detalle text,
    completado boolean NOT NULL,
    prioridad text NOT NULL,
    tipo_gestion text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_recordatorio timestamp with time zone NOT NULL
);


ALTER TABLE public.recordatorio OWNER TO crm_admin;

--
-- Name: recordatorio_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.recordatorio_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recordatorio_id_seq OWNER TO crm_admin;

--
-- Name: recordatorio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.recordatorio_id_seq OWNED BY public.recordatorio.id;


--
-- Name: recordatoriocobranzacuotapoliza; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.recordatoriocobranzacuotapoliza (
    id integer NOT NULL,
    id_cuota integer NOT NULL
);


ALTER TABLE public.recordatoriocobranzacuotapoliza OWNER TO crm_admin;

--
-- Name: recordatoriorenovacionpoliza; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.recordatoriorenovacionpoliza (
    id integer NOT NULL,
    numero_poliza text NOT NULL
);


ALTER TABLE public.recordatoriorenovacionpoliza OWNER TO crm_admin;

--
-- Name: recordatoriousuario; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.recordatoriousuario (
    id integer NOT NULL,
    rut_usuario character varying(10) NOT NULL,
    id_prospecto integer
);


ALTER TABLE public.recordatoriousuario OWNER TO crm_admin;

--
-- Name: rol; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.rol (
    codigo text NOT NULL,
    nombre text NOT NULL
);


ALTER TABLE public.rol OWNER TO crm_admin;

--
-- Name: rolusuario; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.rolusuario (
    rut_usuario character varying(10) NOT NULL,
    codigo_rol text NOT NULL
);


ALTER TABLE public.rolusuario OWNER TO crm_admin;

--
-- Name: solicitudcotizacion; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.solicitudcotizacion (
    id integer NOT NULL,
    fecha timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    prioridad text,
    id_proceso_comercial integer NOT NULL,
    observaciones text,
    tipo text NOT NULL,
    recotizacion boolean DEFAULT false NOT NULL,
    motivo_recotizacion text
);


ALTER TABLE public.solicitudcotizacion OWNER TO crm_admin;

--
-- Name: solicitudcotizacion_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.solicitudcotizacion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.solicitudcotizacion_id_seq OWNER TO crm_admin;

--
-- Name: solicitudcotizacion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.solicitudcotizacion_id_seq OWNED BY public.solicitudcotizacion.id;


--
-- Name: solicitudcotizacionproductoaccidentespersonales; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.solicitudcotizacionproductoaccidentespersonales (
    id integer NOT NULL,
    actividad text CONSTRAINT solicitudcotizacionproductoaccidentespersona_actividad_not_null NOT NULL,
    numero_asegurados integer CONSTRAINT solicitudcotizacionproductoaccidente_numero_asegurados_not_null NOT NULL
);


ALTER TABLE public.solicitudcotizacionproductoaccidentespersonales OWNER TO crm_admin;

--
-- Name: solicitudcotizacionproductoresponsabilidadcivil; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.solicitudcotizacionproductoresponsabilidadcivil (
    id integer NOT NULL,
    limite_responsabilidad_civil real CONSTRAINT solicitudcotizacionproducto_limite_responsabilidad_civ_not_null NOT NULL,
    actividad_del_condominio text CONSTRAINT solicitudcotizacionproductore_actividad_del_condominio_not_null NOT NULL
);


ALTER TABLE public.solicitudcotizacionproductoresponsabilidadcivil OWNER TO crm_admin;

--
-- Name: solicitudcotizacionproductounidades; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.solicitudcotizacionproductounidades (
    id integer NOT NULL,
    monto_asegurado_total real CONSTRAINT solicitudcotizacionproductounida_monto_asegurado_total_not_null NOT NULL,
    nombre_excel text NOT NULL
);


ALTER TABLE public.solicitudcotizacionproductounidades OWNER TO crm_admin;

--
-- Name: solicitudcotizacionproductovidaguardia; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.solicitudcotizacionproductovidaguardia (
    id integer NOT NULL,
    numero_guardias integer NOT NULL
);


ALTER TABLE public.solicitudcotizacionproductovidaguardia OWNER TO crm_admin;

--
-- Name: sucursal; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.sucursal (
    id integer NOT NULL,
    nombre text NOT NULL
);


ALTER TABLE public.sucursal OWNER TO crm_admin;

--
-- Name: sucursal_id_seq; Type: SEQUENCE; Schema: public; Owner: crm_admin
--

CREATE SEQUENCE public.sucursal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sucursal_id_seq OWNER TO crm_admin;

--
-- Name: sucursal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: crm_admin
--

ALTER SEQUENCE public.sucursal_id_seq OWNED BY public.sucursal.id;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: crm_admin
--

CREATE TABLE public.usuario (
    rut character varying(10) NOT NULL,
    nombre text NOT NULL,
    correo text,
    telefono character varying(9),
    id_sucursal integer NOT NULL,
    password_hash text NOT NULL,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    meta_mensual_uf integer,
    habilitado boolean DEFAULT true NOT NULL,
    eliminado boolean DEFAULT false NOT NULL,
    porcentaje_comision real,
    junior boolean DEFAULT false NOT NULL
);


ALTER TABLE public.usuario OWNER TO crm_admin;

--
-- Name: administradorcondominio id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.administradorcondominio ALTER COLUMN id SET DEFAULT nextval('public.administradorcondominio_id_seq'::regclass);


--
-- Name: cierremensual id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cierremensual ALTER COLUMN id SET DEFAULT nextval('public.cierremensual_id_seq'::regclass);


--
-- Name: cliente id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id SET DEFAULT nextval('public.cliente_id_seq'::regclass);


--
-- Name: coberturariesgo id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.coberturariesgo ALTER COLUMN id SET DEFAULT nextval('public.coberturariesgo_id_seq'::regclass);


--
-- Name: coberturatiporiesgo id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.coberturatiporiesgo ALTER COLUMN id SET DEFAULT nextval('public.coberturatiporiesgo_id_seq'::regclass);


--
-- Name: companyseguros id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.companyseguros ALTER COLUMN id SET DEFAULT nextval('public.companyseguros_id_seq'::regclass);


--
-- Name: comunicadogerencia id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.comunicadogerencia ALTER COLUMN id SET DEFAULT nextval('public.comunicadogerencia_id_seq'::regclass);


--
-- Name: cotizacion id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cotizacion ALTER COLUMN id SET DEFAULT nextval('public.cotizacion_id_seq'::regclass);


--
-- Name: cuota id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cuota ALTER COLUMN id SET DEFAULT nextval('public.cuota_id_seq'::regclass);


--
-- Name: estudiocomercialcondominio id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.estudiocomercialcondominio ALTER COLUMN id SET DEFAULT nextval('public.estudiocomercialcondominio_id_seq'::regclass);


--
-- Name: etapaprocesocomercialparticular id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.etapaprocesocomercialparticular ALTER COLUMN id SET DEFAULT nextval('public.etapaprocesocomercialparticular_id_seq'::regclass);


--
-- Name: gestioncomercial id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.gestioncomercial ALTER COLUMN id SET DEFAULT nextval('public.gestioncomercial_id_seq'::regclass);


--
-- Name: historialestadoinformativoprocesocomercial id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.historialestadoinformativoprocesocomercial ALTER COLUMN id SET DEFAULT nextval('public.historialestadoinformativoprocesocomercial_id_seq'::regclass);


--
-- Name: lineanegocio id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.lineanegocio ALTER COLUMN id SET DEFAULT nextval('public.lineanegocio_id_seq'::regclass);


--
-- Name: planpago id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.planpago ALTER COLUMN id SET DEFAULT nextval('public.planpago_id_seq'::regclass);


--
-- Name: procesocomercial id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial ALTER COLUMN id SET DEFAULT nextval('public.procesocomercial_id_seq'::regclass);


--
-- Name: producto id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.producto ALTER COLUMN id SET DEFAULT nextval('public.producto_id_seq'::regclass);


--
-- Name: prospecto id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospecto ALTER COLUMN id SET DEFAULT nextval('public.prospecto_id_seq'::regclass);


--
-- Name: recordatorio id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatorio ALTER COLUMN id SET DEFAULT nextval('public.recordatorio_id_seq'::regclass);


--
-- Name: solicitudcotizacion id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacion ALTER COLUMN id SET DEFAULT nextval('public.solicitudcotizacion_id_seq'::regclass);


--
-- Name: sucursal id; Type: DEFAULT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.sucursal ALTER COLUMN id SET DEFAULT nextval('public.sucursal_id_seq'::regclass);


--
-- Data for Name: administradorcondominio; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.administradorcondominio (id, nombre_administrador, nombre_contacto, telefono, correo) FROM stdin;
1	Administración de Condominios SpA	Juan Pérez	+56985258525	administracion_spa@correo.cl
2	Empresa Administradora de Condominios	Juan Pérez	+56954218794	c@mail.com
\.


--
-- Data for Name: cierremensual; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.cierremensual (id, year, mes, fecha_cierre, valor_uf_cierre, cerrado_por) FROM stdin;
\.


--
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.cliente (id, id_prospecto, rut_ej_renovacion_asignado, rut_as_renovacion_asignado, rut_ej_cobranza_asignado) FROM stdin;
96	113	\N	\N	\N
97	115	\N	\N	\N
98	118	\N	\N	\N
47	61	13358892-2	19041141-9	\N
48	62	13358892-2	19041141-9	\N
49	63	13358892-2	19041141-9	\N
50	64	13358892-2	19041141-9	\N
51	65	13358892-2	19041141-9	\N
52	66	13358892-2	19041141-9	\N
53	67	13358892-2	19041141-9	\N
54	68	13358892-2	19041141-9	\N
55	69	13358892-2	19041141-9	\N
56	70	13358892-2	19041141-9	\N
57	71	13358892-2	19041141-9	\N
58	72	13358892-2	19041141-9	\N
59	73	13358892-2	19041141-9	\N
60	74	13358892-2	19041141-9	\N
61	75	13358892-2	19041141-9	\N
62	76	13358892-2	19041141-9	\N
63	77	13358892-2	19041141-9	\N
64	78	13358892-2	19041141-9	\N
65	79	13358892-2	19041141-9	\N
66	80	13358892-2	19041141-9	\N
67	81	13358892-2	19041141-9	\N
68	82	13358892-2	19041141-9	\N
69	83	13358892-2	19041141-9	\N
70	84	13358892-2	19041141-9	\N
71	85	13358892-2	19041141-9	\N
72	86	13358892-2	19041141-9	\N
73	87	13358892-2	19041141-9	\N
74	88	13358892-2	19041141-9	\N
75	89	13358892-2	19041141-9	\N
76	90	13358892-2	19041141-9	\N
77	91	13358892-2	19041141-9	\N
78	92	13358892-2	19041141-9	\N
79	93	13358892-2	19041141-9	\N
80	94	13358892-2	19041141-9	\N
81	95	13358892-2	19041141-9	\N
82	96	13358892-2	19041141-9	\N
83	97	13358892-2	19041141-9	\N
84	98	13358892-2	19041141-9	\N
85	99	13358892-2	19041141-9	\N
86	100	13358892-2	19041141-9	\N
87	101	13358892-2	19041141-9	\N
88	102	13358892-2	19041141-9	\N
89	103	13358892-2	19041141-9	\N
90	104	13358892-2	19041141-9	\N
91	105	13358892-2	19041141-9	\N
92	106	13358892-2	19041141-9	\N
93	8	13358892-2	19041141-9	\N
94	7	13358892-2	19041141-9	\N
95	112	13358892-2	19041141-9	\N
\.


--
-- Data for Name: coberturariesgo; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.coberturariesgo (id, id_cobertura_tipo_riesgo, nombre) FROM stdin;
1	1	Incendio y daños materiales a consecuencia directa de huelga, saqueo o desorden popular
2	1	Actos Terroristas
3	2	Daños materiales causados por avalancha, aluviones y deslizamientos
4	2	Incendio y daños materiales causados por erupción volcánica
5	2	Incendio y daños materiales causados por maremoto, Tsunami y salida de mar
6	2	Daños materiales causados por peso de nieve o hielo
7	2	Daños materiales a causa de viento, inundación y desbordamiento de cauces
8	3	Incendio y daños materiales por sismo
9	4	Incendio y daños materiales causados por caída y colisión de aeronaves
10	4	Colapso de Edificios
11	4	Incendio y daños materiales causados por Combustión Espontánea
12	4	Daños materiales causados por construcción o demolición de edificios colindantes
13	4	Daños materiales causados por explosión
14	4	Incendio y daños materiales causados por colisión de objetos flotantes
15	4	Daños materiales causados por roturas de cañerías, desagües y por desbordamiento de estanques
16	4	Incendio y daños materiales causados por colisión de vehículos
17	5	Rotura de Cristales
18	5	Instalaciones Electrónicas
19	5	Avería de Maquinaria
20	5	Responsabilidad Civil Propietario Inmueble
21	5	Robo con Fuerza en las cosas
22	5	Robo con Violencia en las Persona
23	5	Accidentes Personales
24	5	Remesas de Valores
25	6	Incorporacion de activos nuevos
26	6	Gastos de Aceleración
27	6	Gastos por Obtención de Permisos y Orden de Reconstrucción Municipal
28	6	Bienes e Intereses de Terceros
29	6	Bienes de empleados (trabajadores de la comunidad)
30	6	Sprinklers
31	6	Trabajos de construcción, reparación y manutención
32	6	Cláusula de Eventual Mayor Valor (Infraseguro, Bienes Físicos)
33	6	Costo de alivio de pérdida y/o gastos de salvamento
34	6	Reparaciones Provisorias
35	6	Rehabilitación automática
36	6	Honorarios Profesionales
37	6	Daño Eléctrico
38	6	Valor de Reposición a Nuevo
39	6	Cláusula 72 Horas
40	6	Remoción de Escombros
41	6	Asistencia para Bienes y Espacios Comunes
\.


--
-- Data for Name: coberturatiporiesgo; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.coberturatiporiesgo (id, nombre) FROM stdin;
1	Riesgos Políticos
2	Riesgos de la Naturaleza
3	Sismo
4	Otros Adicionales
5	Coberturas Complementarias
6	Coberturas Especiales
\.


--
-- Data for Name: companiessugeridas; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.companiessugeridas (id_prospecto, id_company) FROM stdin;
\.


--
-- Data for Name: companycoberturariesgo; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.companycoberturariesgo (id_company_seguro, id_cobertura_riesgo, descripcion) FROM stdin;
\.


--
-- Data for Name: companyseguros; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.companyseguros (id, nombre) FROM stdin;
1	Renta Nacional
2	Renta Nacional ANS
3	Sura Seguros
4	BCI Seguros
5	BCI Seguros ANS
6	Liberty Seguros
7	Consorcio
8	HDI Seguros
9	FID Seguros
10	Mapfre Seguros
11	Mapfre Seguros ANS
12	Zurich
13	Reale
14	Chubb
15	Sura
\.


--
-- Data for Name: comunicadogerencia; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.comunicadogerencia (id, rut_gerente, titulo, descripcion, prioridad, fecha, caducidad) FROM stdin;
1	20036887-8	Reunión comercial	Hoy a las 16:00 se realizará una reunión breve de seguimiento comercial.	Normal	2026-06-01 14:12:40.570966+00	2026-06-01 20:00:00+00
2	20036887-8	Compañías sugeridas	Durante esta semana se sugiere cotizar en BCI y HDI debido a nuevos convenios.	Alta	2026-06-01 14:14:42.392225+00	2026-06-06 03:59:00+00
3	20036887-8	Preferencia compañias	Cotizar en BCI y Zurich	alta	2026-07-03 21:14:29.709431+00	2026-07-31 00:00:00+00
\.


--
-- Data for Name: cotizacion; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.cotizacion (id, id_company, fecha_emision, fecha_vencimiento, monto_total_asegurado, prima_adicional_asistencia, tasa_afecta, tasa_excenta, tasa_politica, id_solicitud, nombre_archivo) FROM stdin;
1	4	2026-06-14 04:00:00+00	2026-06-24 04:00:00+00	319560	0.7	0.3	1.4	0	1	\N
3	10	2026-06-15 04:00:00+00	2026-06-25 04:00:00+00	319560	0.6	0.5	1.3	0	1	\N
2	8	2026-06-14 04:00:00+00	2026-06-26 04:00:00+00	319560	0.5	0.4	1.5	0	1	\N
6	1	2026-06-16 14:15:00+00	2026-06-30 21:15:00+00	450	0	0.2	0.9	0	114	\N
7	10	2026-06-16 14:15:00+00	2026-06-30 21:15:00+00	450	0	0.32	1.2	0	114	\N
8	7	2026-06-19 00:00:00+00	2026-07-03 00:00:00+00	1500	0	0	0.24	1.5	119	\N
9	1	2026-06-19 00:00:00+00	2026-06-25 00:00:00+00	200	0.3	0.5	1.25	0	121	\N
10	4	2026-06-19 00:00:00+00	2026-06-21 00:00:00+00	200	0	0.3	1.7	0.2	121	\N
11	15	2026-06-22 00:00:00+00	2026-07-03 00:00:00+00	200	0	0.2	1.2	0	118	\N
12	4	2026-06-22 00:00:00+00	2026-06-29 00:00:00+00	100000	0.2	0.5	0.9	0.1	116	\N
13	1	2026-06-23 00:00:00+00	2026-07-06 00:00:00+00	100	0	0.2	1.1	0	125	\N
14	9	2026-06-23 00:00:00+00	2026-07-03 00:00:00+00	100	0	0.3	0.9	0.1	125	\N
15	8	2026-06-30 00:00:00+00	2026-07-07 00:00:00+00	320000	0.6	0.3	1.2	0	126	\N
16	4	2026-06-30 00:00:00+00	2026-07-10 00:00:00+00	320000	0	0.5	1.3	0	126	\N
17	6	2026-06-30 00:00:00+00	2026-07-07 00:00:00+00	256000	0	0.3	1.2	0	127	\N
18	7	2026-06-30 00:00:00+00	2026-07-14 00:00:00+00	256000	0	0.25	1.12	0.1	127	\N
19	10	2026-06-30 00:00:00+00	2026-07-10 00:00:00+00	120000	0	0.23	1.1	0	128	cotizacion_128_870bc79f211a43d0939e68799fa2dc12.pdf
20	12	2026-06-26 00:00:00+00	2026-07-04 00:00:00+00	330000	0	0.31	1.26	0	130	cotizacion_130_cc5d22f115744a2d808959e425350d73.pdf
21	9	2026-04-20 00:00:00+00	2026-09-28 00:00:00+00	330000	4	0.2	1.21	0.1	130	cotizacion_130_bc027ff6112b4204839b156835ae742b.pdf
22	12	2026-07-01 00:00:00+00	2026-07-15 00:00:00+00	330000	0	0.32	1.26	0	132	\N
23	9	2026-07-01 00:00:00+00	2026-07-10 00:00:00+00	330000	4	0.2	1.21	0.1	132	\N
24	9	2026-07-02 00:00:00+00	2026-07-16 00:00:00+00	330000	4	0.2	1.21	0.1	133	cotizacion_133_78981ddf9697450289b0fb678acdfd1c.pdf
25	12	2026-07-02 00:00:00+00	2026-07-10 00:00:00+00	330000	0	0.32	1.26	0	133	cotizacion_133_aedb218ea6da48908cce3d2ac36ecf27.pdf
26	9	2026-07-02 00:00:00+00	2026-07-16 00:00:00+00	330000	0	0.2	1.21	0.1	134	\N
27	9	2026-07-02 00:00:00+00	2026-07-16 00:00:00+00	330000	4	0.2	1.21	0.1	134	\N
28	12	2026-07-02 00:00:00+00	2026-07-08 00:00:00+00	330000	0	0.32	1.26	0	134	\N
29	10	2026-07-03 00:00:00+00	2026-07-10 00:00:00+00	330000	0	0.2	1.5	0	134	\N
30	4	2026-07-03 00:00:00+00	2026-07-10 00:00:00+00	100	0	0.15	1.1	0	136	cotizacion_136_1308984485a24ad083ba5f1ea221b1eb.pdf
31	14	2026-07-04 00:00:00+00	2026-07-17 00:00:00+00	300	0	0.1	0.1	0	137	\N
32	9	2026-07-06 00:00:00+00	2026-07-20 00:00:00+00	1000	0	0.2	1	0	139	\N
33	9	2026-07-06 00:00:00+00	2026-07-20 00:00:00+00	60000	0	0.2	1.2	0	140	\N
34	1	2026-07-06 00:00:00+00	2026-07-20 00:00:00+00	268000	0	0.16	1.27	0.13	141	cotizacion_141_c9f6c52c7c9445d3a13294b6f7e2de03.pdf
36	12	2026-07-06 00:00:00+00	2026-07-20 00:00:00+00	780000	0	0.35	1.4	0	142	cotizacion_142_b96fa3541d3e4ba281b9f35957b7b098.pdf
37	7	2026-07-06 00:00:00+00	2026-07-17 00:00:00+00	780000	1	0.2	1.23	0	142	\N
\.


--
-- Data for Name: cuota; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.cuota (id, id_plan_pago, numero_cuota, fecha_vencimiento, pagado, fecha_pago) FROM stdin;
12	2	1	2025-07-05 04:00:00+00	t	2025-07-05 12:17:32+00
13	2	2	2025-08-05 04:00:00+00	t	2025-08-05 18:42:11+00
14	2	3	2025-09-05 04:00:00+00	t	2025-09-05 13:05:47+00
15	2	4	2025-10-05 03:00:00+00	t	2025-10-05 19:28:53+00
16	2	5	2025-11-05 03:00:00+00	t	2025-11-05 14:56:18+00
17	2	6	2025-12-05 03:00:00+00	t	2025-12-05 21:09:41+00
18	2	7	2026-01-05 03:00:00+00	t	2026-01-05 13:34:26+00
19	2	8	2026-02-05 03:00:00+00	t	2026-02-05 18:21:09+00
20	2	9	2026-03-05 03:00:00+00	t	2026-03-05 16:48:55+00
21	2	10	2026-04-05 04:00:00+00	t	2026-04-05 21:15:37+00
22	2	11	2026-05-05 04:00:00+00	t	2026-05-05 13:58:14+00
23	3	1	2026-07-05 00:00:00+00	f	\N
24	3	2	2026-08-05 00:00:00+00	f	\N
25	3	3	2026-09-05 00:00:00+00	f	\N
26	3	4	2026-10-05 00:00:00+00	f	\N
27	3	5	2026-11-05 00:00:00+00	f	\N
28	3	6	2026-12-05 00:00:00+00	f	\N
29	3	7	2027-01-05 00:00:00+00	f	\N
30	3	8	2027-02-05 00:00:00+00	f	\N
31	3	9	2027-03-05 00:00:00+00	f	\N
32	3	10	2027-04-05 00:00:00+00	f	\N
33	3	11	2027-05-05 00:00:00+00	f	\N
34	4	1	2026-08-01 00:00:00+00	f	\N
35	4	2	2026-09-01 00:00:00+00	f	\N
36	4	3	2026-10-01 00:00:00+00	f	\N
37	4	4	2026-11-01 00:00:00+00	f	\N
38	4	5	2026-12-01 00:00:00+00	f	\N
39	4	6	2027-01-01 00:00:00+00	f	\N
40	4	7	2027-02-01 00:00:00+00	f	\N
41	4	8	2027-03-01 00:00:00+00	f	\N
42	4	9	2027-04-01 00:00:00+00	f	\N
43	4	10	2027-05-01 00:00:00+00	f	\N
44	4	11	2027-06-01 00:00:00+00	f	\N
45	5	1	2026-07-30 00:00:00+00	f	\N
46	5	2	2026-08-30 00:00:00+00	f	\N
47	5	3	2026-09-30 00:00:00+00	f	\N
48	5	4	2026-10-30 00:00:00+00	f	\N
49	5	5	2026-11-30 00:00:00+00	f	\N
50	5	6	2026-12-30 00:00:00+00	f	\N
51	5	7	2027-01-30 00:00:00+00	f	\N
52	5	8	2027-02-28 00:00:00+00	f	\N
53	5	9	2027-03-30 00:00:00+00	f	\N
54	5	10	2027-04-30 00:00:00+00	f	\N
55	5	11	2027-05-30 00:00:00+00	f	\N
56	6	1	2026-08-05 00:00:00+00	f	\N
57	6	2	2026-09-05 00:00:00+00	f	\N
58	6	3	2026-10-05 00:00:00+00	f	\N
59	6	4	2026-11-05 00:00:00+00	f	\N
60	6	5	2026-12-05 00:00:00+00	f	\N
61	6	6	2027-01-05 00:00:00+00	f	\N
62	6	7	2027-02-05 00:00:00+00	f	\N
63	6	8	2027-03-05 00:00:00+00	f	\N
64	6	9	2027-04-05 00:00:00+00	f	\N
65	6	10	2027-05-05 00:00:00+00	f	\N
66	6	11	2027-06-05 00:00:00+00	f	\N
67	7	1	2026-07-30 00:00:00+00	f	\N
68	7	2	2026-08-30 00:00:00+00	f	\N
69	7	3	2026-09-30 00:00:00+00	f	\N
70	7	4	2026-10-30 00:00:00+00	f	\N
71	7	5	2026-11-30 00:00:00+00	f	\N
72	7	6	2026-12-30 00:00:00+00	f	\N
73	7	7	2027-01-30 00:00:00+00	f	\N
74	7	8	2027-02-28 00:00:00+00	f	\N
75	7	9	2027-03-30 00:00:00+00	f	\N
76	7	10	2027-04-30 00:00:00+00	f	\N
77	7	11	2027-05-30 00:00:00+00	f	\N
\.


--
-- Data for Name: detallecierremensual; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.detallecierremensual (id_cierre_mensual, rut_ejecutivo, numero_poliza, comision_corredora_uf, pct_comision_ejecutivo, comision_uf, comision_pesos) FROM stdin;
\.


--
-- Data for Name: estadoinformativoprocesocomercial; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.estadoinformativoprocesocomercial (codigo, codigo_etapa, nombre) FROM stdin;
CONTACTADO	GESTIONANDO_OPORTUNIDAD	Contactado
ESTUDIO_DISPONIBLE	GESTIONANDO_OPORTUNIDAD	Estudio disponible
RECOTIZACION_SOLICITADA	GESTIONANDO_OPORTUNIDAD	Recotizacion solicitada
CLIENTE_CARGADO_MASIVO	CERRADO	Cliente cargado desde archivo excel
GANADO	CERRADO	Ganado
PERDIDO	CERRADO	Perdido
COTIZACION_SOLICITADA_COMPANY	GESTIONANDO_OPORTUNIDAD	Cotización solicitada
ESTUDIO_ENVIADO_CLIENTE	GESTIONANDO_OPORTUNIDAD	Estudio enviado al cliente
EJECUTIVO_COMERCIAL_ASIGNADO	GESTION_INICIAL	Ejecutivo comercial asignado
OPORTUNIDAD_CREADA	GESTION_INICIAL	Oportunidad creada
PROPUESTA_ACEPTADA	FORMALIZACION	Propuesta aceptada
POLIZA_REGISTRADA	FORMALIZACION	Póliza registrada
PLAN_PAGO_CREADO	FORMALIZACION	Plan de pago creado
COTIZACION_DISPONIBLE	GESTIONANDO_OPORTUNIDAD	Cotización disponible
\.


--
-- Data for Name: estudiocomercialcondominio; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.estudiocomercialcondominio (id, id_solicitud, nombre_archivo) FROM stdin;
1	134	estudio_comercial_134_1783285898109.pdf
2	134	estudio_comercial_134_1783289202985.pdf
3	141	estudio_comercial_141_1783353963317.pdf
4	141	estudio_comercial_141_1783354589482.pdf
5	142	estudio_comercial_142_1783356223951.pdf
\.


--
-- Data for Name: etapaprocesocomercial; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.etapaprocesocomercial (codigo, nombre, codigo_siguiente_etapa, dias_limite, es_terminal) FROM stdin;
GESTION_INICIAL	En planificación	GESTIONANDO_OPORTUNIDAD	2	f
CERRADO	Oportunidad cerrada	\N	\N	t
FORMALIZACION	Formalización	CERRADO	14	f
GESTIONANDO_OPORTUNIDAD	Gestionando oportunidad	\N	7	f
\.


--
-- Data for Name: etapaprocesocomercialparticular; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.etapaprocesocomercialparticular (id, id_proceso_comercial, codigo_etapa, dias_limite_particular) FROM stdin;
\.


--
-- Data for Name: factorcuotascompany; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.factorcuotascompany (id_company, numero_cuotas, factor) FROM stdin;
13	1	1.00526
13	2	0.50438
13	3	0.33327
13	4	0.25131
13	5	0.203
13	6	0.1696
13	7	0.1457
13	8	0.1278
13	9	0.1139
13	10	0.1028
13	11	0.0937
8	1	0
8	2	0.5046
8	3	0.3372
8	4	0.2534
8	5	0.2032
8	6	0.1697
8	7	0.1458
8	8	0.1279
8	9	0.1139
8	10	0.1028
8	11	0.0936
8	12	0.086
1	1	1.005475
1	2	0.5041645
1	3	0.3370385
1	4	0.2534768
1	5	0.2033408
1	6	0.1699876
1	7	0.1460447
1	8	0.1281406
1	9	0.1142158
1	10	0.1030764
1	11	0.0939809
1	12	0.0863687
14	1	1
14	2	0.5045
14	3	0.3373
14	4	0.2533
14	5	0.2036
14	6	0.1702
14	7	0.1463
14	8	0.1284
14	9	0.1141
14	10	0.1033
4	1	1.0032
4	2	0.5024
4	3	0.3355
4	4	0.252
4	5	0.2019
4	6	0.1688
4	7	0.1447
4	8	0.1268
4	9	0.1129
4	10	0.1018
4	11	0.0927
10	10	0.1029
10	11	0.0938
10	12	0.0862
\.


--
-- Data for Name: gestioncomercial; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.gestioncomercial (id, tipo, rut_usuario, id_prospecto, titulo, estado_contacto, observacion, created_at, fecha_gestion) FROM stdin;
1	llamada	19995707-4	118	Llamada	\N	\N	2026-07-06 21:15:00.086958+00	2026-07-06 17:14:00+00
\.


--
-- Data for Name: historialestadoinformativoprocesocomercial; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.historialestadoinformativoprocesocomercial (id, id_proceso_comercial, codigo_estado, fecha_registro, observacion, rut_registrado_por) FROM stdin;
164	6	CONTACTADO	2026-05-29 12:15:26.664163+00	\N	16517406-2
165	6	COTIZACION_SOLICITADA_COMPANY	2026-06-02 14:15:26.664163+00	\N	16517406-2
108	122	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
109	123	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
110	124	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
111	125	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
112	126	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
116	130	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
118	132	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
119	133	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
120	134	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
121	135	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
122	136	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
129	143	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
130	144	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
131	145	GANADO	2026-06-05 19:50:25.926916+00	\N	16517406-2
303	310	OPORTUNIDAD_CREADA	2026-06-25 17:35:14.962881+00	\N	16517406-2
304	310	GANADO	2026-06-25 17:36:06.567602+00	\N	16517406-2
163	6	EJECUTIVO_COMERCIAL_ASIGNADO	2026-05-28 13:00:26.664163+00	\N	20036887-8
305	311	OPORTUNIDAD_CREADA	2026-06-25 17:36:38.779461+00	\N	16517406-2
306	311	GANADO	2026-06-25 17:37:05.306582+00	\N	16517406-2
308	312	COTIZACION_SOLICITADA_COMPANY	2026-06-30 13:47:43.949936+00	\N	16517406-2
311	312	GANADO	2026-06-30 14:51:48.145634+00	\N	16517406-2
113	127	GANADO	2026-06-05 19:50:25.926916+00	\N	21036887-1
132	146	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
133	147	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
134	148	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
126	140	GANADO	2026-06-05 19:50:25.926916+00	\N	21036887-3
127	141	GANADO	2026-06-05 19:50:25.926916+00	\N	21036887-3
128	142	GANADO	2026-06-05 19:50:25.926916+00	\N	21036887-3
135	149	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
136	150	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
143	157	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
144	158	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
104	118	GANADO	2026-06-05 19:50:25.926916+00	\N	19995707-4
105	119	GANADO	2026-06-05 19:50:25.926916+00	\N	19995707-4
106	120	GANADO	2026-06-05 19:50:25.926916+00	\N	19995707-4
107	121	GANADO	2026-06-05 19:50:25.926916+00	\N	19995707-4
114	128	GANADO	2026-06-05 19:50:25.926916+00	\N	19995707-4
115	129	GANADO	2026-06-05 19:50:25.926916+00	\N	19995707-4
117	131	GANADO	2026-06-05 19:50:25.926916+00	\N	19995707-4
137	151	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
138	152	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
139	153	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
140	154	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
141	155	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
142	156	GANADO	2026-06-05 19:50:25.926916+00	\N	19956311-4
123	137	GANADO	2026-06-05 19:50:25.926916+00	\N	28372975-3
124	138	GANADO	2026-06-05 19:50:25.926916+00	\N	28372975-3
125	139	GANADO	2026-06-05 19:50:25.926916+00	\N	28372975-3
166	6	COTIZACION_DISPONIBLE	2026-06-05 14:15:26.664163+00	\N	19661132-0
378	332	COTIZACION_DISPONIBLE	2026-07-06 15:11:47.998888+00	\N	19956311-4
381	333	COTIZACION_DISPONIBLE	2026-07-06 16:01:38.367235+00	\N	19956311-4
384	334	OPORTUNIDAD_CREADA	2026-07-06 16:24:45.116123+00	\N	19956311-4
389	334	PROPUESTA_ACEPTADA	2026-07-06 16:44:13.794574+00	\N	20036887-8
240	293	COTIZACION_SOLICITADA_COMPANY	2026-06-16 21:53:06.764099+00	\N	16517406-2
243	295	COTIZACION_SOLICITADA_COMPANY	2026-06-17 13:53:38.55994+00	\N	16517406-2
244	293	RECOTIZACION_SOLICITADA	2026-06-17 14:20:02.994965+00	\N	16517406-2
248	296	COTIZACION_SOLICITADA_COMPANY	2026-06-18 23:20:05.954964+00	\N	16517406-2
249	297	COTIZACION_SOLICITADA_COMPANY	2026-06-18 23:29:17.872745+00	\N	16517406-2
254	299	COTIZACION_SOLICITADA_COMPANY	2026-06-19 18:02:41.014157+00	\N	16517406-2
266	301	OPORTUNIDAD_CREADA	2026-06-21 22:04:10.354414+00	\N	16517406-2
267	302	OPORTUNIDAD_CREADA	2026-06-21 22:05:02.27595+00	\N	16517406-2
268	302	COTIZACION_SOLICITADA_COMPANY	2026-06-21 22:46:49.340845+00	\N	16517406-2
279	6	GANADO	2026-06-23 16:35:47.40653+00	\N	16517406-2
280	296	GANADO	2026-06-23 16:37:52.803459+00	\N	16517406-2
281	303	OPORTUNIDAD_CREADA	2026-06-23 16:45:11.476869+00	\N	16517406-2
282	303	COTIZACION_SOLICITADA_COMPANY	2026-06-23 16:45:57.30611+00	\N	16517406-2
286	303	GANADO	2026-06-23 16:52:52.176806+00	\N	16517406-2
291	304	OPORTUNIDAD_CREADA	2026-06-25 16:04:24.169837+00	\N	16517406-2
292	304	GANADO	2026-06-25 16:05:46.062797+00	\N	16517406-2
299	308	OPORTUNIDAD_CREADA	2026-06-25 17:32:46.807895+00	\N	16517406-2
300	308	GANADO	2026-06-25 17:33:24.029849+00	\N	16517406-2
301	309	OPORTUNIDAD_CREADA	2026-06-25 17:33:52.376723+00	\N	16517406-2
293	305	OPORTUNIDAD_CREADA	2026-06-25 16:16:53.192528+00	\N	19956311-4
294	305	GANADO	2026-06-25 16:18:06.834824+00	\N	19956311-4
295	306	OPORTUNIDAD_CREADA	2026-06-25 16:19:07.013018+00	\N	19956311-4
247	293	ESTUDIO_DISPONIBLE	2026-06-18 22:03:25.331164+00	\N	20036887-8
259	299	PERDIDO	2026-06-21 17:09:32.716326+00	\N	20036887-8
296	306	GANADO	2026-06-25 16:19:51.290697+00	\N	19956311-4
297	307	OPORTUNIDAD_CREADA	2026-06-25 16:21:04.106198+00	\N	19956311-4
262	297	GANADO	2026-06-21 17:51:19.24041+00	El cliente envió la aceptación	20036887-8
263	300	OPORTUNIDAD_CREADA	2026-06-21 19:17:21.411344+00	\N	20036887-8
269	293	GANADO	2026-06-22 00:06:42.22157+00	Aceptación recibida	20036887-8
270	302	PERDIDO	2026-06-22 14:47:04.243415+00	\N	20036887-8
298	307	GANADO	2026-06-25 16:21:34.153716+00	\N	19956311-4
326	317	OPORTUNIDAD_CREADA	2026-06-30 20:23:45.421728+00	\N	19956311-4
323	315	OPORTUNIDAD_CREADA	2026-06-30 20:05:03.431363+00	\N	19956311-4
324	315	COTIZACION_SOLICITADA_COMPANY	2026-06-30 20:06:05.616116+00	\N	19956311-4
277	295	PROPUESTA_ACEPTADA	2026-06-22 20:38:11.123075+00	\N	20036887-8
278	295	GANADO	2026-06-23 15:23:10.326351+00	\N	20036887-8
325	316	OPORTUNIDAD_CREADA	2026-06-30 20:22:30.731258+00	\N	19956311-4
327	318	OPORTUNIDAD_CREADA	2026-06-30 20:23:59.327564+00	\N	19956311-4
285	303	PROPUESTA_ACEPTADA	2026-06-23 16:51:39.809905+00	\N	20036887-8
288	300	PROPUESTA_ACEPTADA	2026-06-23 20:23:41.582121+00	\N	20036887-8
290	301	PERDIDO	2026-06-25 15:01:44.761074+00	Negocio no prosperó	20036887-8
302	309	PERDIDO	2026-06-25 17:35:00.170419+00	\N	20036887-8
307	312	OPORTUNIDAD_CREADA	2026-06-30 13:34:03.635178+00	\N	20036887-8
328	319	OPORTUNIDAD_CREADA	2026-06-30 20:24:38.582243+00	\N	19956311-4
329	319	COTIZACION_SOLICITADA_COMPANY	2026-06-30 20:24:53.969505+00	\N	19956311-4
334	319	POLIZA_REGISTRADA	2026-06-30 21:00:38.341692+00	\N	19956311-4
315	313	PROPUESTA_ACEPTADA	2026-06-30 16:33:03.261164+00	\N	20036887-8
335	319	PLAN_PAGO_CREADO	2026-06-30 21:02:11.374643+00	\N	19956311-4
150	164	GANADO	2026-06-05 19:50:25.926916+00	\N	15634751-5
151	165	GANADO	2026-06-05 19:50:25.926916+00	\N	15634751-5
251	298	COTIZACION_SOLICITADA_COMPANY	2026-06-19 16:02:52.393304+00	\N	19995707-4
376	332	OPORTUNIDAD_CREADA	2026-07-06 15:08:23.832453+00	\N	19956311-4
379	333	OPORTUNIDAD_CREADA	2026-07-06 16:00:34.639087+00	\N	19956311-4
241	293	COTIZACION_DISPONIBLE	2026-06-16 21:54:15.202222+00	\N	19661132-0
252	297	COTIZACION_DISPONIBLE	2026-06-19 17:52:46.893462+00	\N	19661132-0
255	299	COTIZACION_DISPONIBLE	2026-06-19 18:07:59.308377+00	\N	19661132-0
250	6	ESTUDIO_DISPONIBLE	2026-06-19 14:23:50.560859+00	\N	19661132-0
253	297	ESTUDIO_DISPONIBLE	2026-06-19 17:53:41.286728+00	\N	19661132-0
256	299	ESTUDIO_DISPONIBLE	2026-06-19 18:09:04.783532+00	\N	19661132-0
258	299	ESTUDIO_DISPONIBLE	2026-06-19 18:12:11.140724+00	\N	19661132-0
264	300	COTIZACION_SOLICITADA_COMPANY	2026-06-21 20:09:49.285648+00	\N	19995707-4
265	300	RECOTIZACION_SOLICITADA	2026-06-21 20:23:09.381676+00	\N	19995707-4
287	298	GANADO	2026-06-23 20:19:40.6562+00	\N	19995707-4
289	300	GANADO	2026-06-25 14:59:37.874037+00	\N	19995707-4
312	313	OPORTUNIDAD_CREADA	2026-06-30 16:22:51.494267+00	\N	19995707-4
313	313	COTIZACION_SOLICITADA_COMPANY	2026-06-30 16:28:50.400469+00	\N	19995707-4
316	313	POLIZA_REGISTRADA	2026-06-30 16:33:58.22566+00	\N	19995707-4
317	313	PLAN_PAGO_CREADO	2026-06-30 17:01:56.227227+00	\N	19995707-4
318	313	GANADO	2026-06-30 17:01:56.313824+00	\N	19995707-4
319	314	OPORTUNIDAD_CREADA	2026-06-15 18:46:04.637878+00	\N	19995707-4
320	314	COTIZACION_SOLICITADA_COMPANY	2026-06-19 18:46:04.637878+00	\N	19995707-4
257	299	COTIZACION_DISPONIBLE	2026-06-19 18:11:46.653972+00	\N	19661132-0
271	296	COTIZACION_DISPONIBLE	2026-06-22 16:12:17.643901+00	\N	19661132-0
272	295	COTIZACION_DISPONIBLE	2026-06-22 17:03:32.464019+00	\N	19661132-0
382	333	ESTUDIO_DISPONIBLE	2026-07-06 16:16:29.516618+00	\N	19956311-4
385	334	COTIZACION_SOLICITADA_COMPANY	2026-07-06 16:25:10.857743+00	\N	19956311-4
387	334	COTIZACION_DISPONIBLE	2026-07-06 16:29:40.835434+00	\N	19661132-0
390	323	PLAN_PAGO_CREADO	2026-07-06 19:59:31.841212+00	\N	20036887-8
341	320	ESTUDIO_DISPONIBLE	2026-07-01 16:18:38.293659+00	\N	20036887-8
145	159	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
146	160	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
147	161	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
148	162	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
149	163	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
152	166	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
153	167	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
154	168	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
155	169	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
156	170	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
157	171	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
158	172	GANADO	2026-06-05 19:50:25.926916+00	\N	12220101-5
332	314	PROPUESTA_ACEPTADA	2026-06-30 20:55:45.602932+00	\N	12220101-5
333	315	PERDIDO	2026-06-30 20:58:08.521827+00	\N	12220101-5
273	295	ESTUDIO_DISPONIBLE	2026-06-22 17:03:57.308383+00	\N	19661132-0
284	303	ESTUDIO_DISPONIBLE	2026-06-23 16:51:01.646333+00	\N	19661132-0
310	312	ESTUDIO_DISPONIBLE	2026-06-30 14:47:25.803849+00	\N	19661132-0
331	319	ESTUDIO_DISPONIBLE	2026-06-30 20:38:01.579242+00	\N	19661132-0
391	323	GANADO	2026-07-06 19:59:31.954174+00	\N	20036887-8
345	321	ESTUDIO_DISPONIBLE	2026-07-02 19:28:27.31304+00	\N	19661132-0
349	322	ESTUDIO_DISPONIBLE	2026-07-02 19:47:35.692221+00	\N	19661132-0
363	325	OPORTUNIDAD_CREADA	2026-07-04 21:18:25.540715+00	\N	19661132-0
364	325	COTIZACION_SOLICITADA_COMPANY	2026-07-04 21:25:05.987412+00	\N	19661132-0
366	325	ESTUDIO_DISPONIBLE	2026-07-04 21:31:12.592639+00	\N	19661132-0
367	326	OPORTUNIDAD_CREADA	2026-07-04 21:31:20.940241+00	\N	19661132-0
368	326	COTIZACION_SOLICITADA_COMPANY	2026-07-04 21:31:29.368362+00	\N	19661132-0
370	328	OPORTUNIDAD_CREADA	2026-07-06 14:40:44.909781+00	\N	20036887-8
371	329	OPORTUNIDAD_CREADA	2026-07-06 14:40:47.974918+00	\N	20036887-8
372	330	OPORTUNIDAD_CREADA	2026-07-06 14:40:53.490513+00	\N	20036887-8
373	331	OPORTUNIDAD_CREADA	2026-07-06 14:40:56.360865+00	\N	20036887-8
346	322	OPORTUNIDAD_CREADA	2026-07-02 19:41:10.797683+00	\N	19995707-4
347	322	COTIZACION_SOLICITADA_COMPANY	2026-07-02 19:41:21.831638+00	\N	19995707-4
350	322	COTIZACION_SOLICITADA_COMPANY	2026-07-03 17:58:46.958532+00	\N	19995707-4
351	322	ESTUDIO_DISPONIBLE	2026-07-03 18:39:09.23884+00	\N	19995707-4
353	322	ESTUDIO_DISPONIBLE	2026-07-03 18:39:52.695004+00	\N	19995707-4
354	314	POLIZA_REGISTRADA	2026-07-03 19:44:28.663752+00	\N	19995707-4
355	314	PLAN_PAGO_CREADO	2026-07-03 19:45:37.391997+00	\N	19995707-4
356	314	GANADO	2026-07-03 19:45:37.485456+00	\N	19995707-4
357	323	OPORTUNIDAD_CREADA	2026-07-03 21:37:55.346897+00	\N	19995707-4
358	323	COTIZACION_SOLICITADA_COMPANY	2026-07-03 21:38:16.559957+00	\N	19995707-4
360	323	POLIZA_REGISTRADA	2026-07-03 21:40:05.540526+00	\N	19995707-4
361	324	OPORTUNIDAD_CREADA	2026-07-03 21:43:47.535183+00	\N	19995707-4
362	324	POLIZA_REGISTRADA	2026-07-03 21:44:19.918165+00	\N	19995707-4
369	327	OPORTUNIDAD_CREADA	2026-07-04 21:54:26.93063+00	\N	19995707-4
338	320	OPORTUNIDAD_CREADA	2026-07-01 14:07:37.222198+00	\N	16517406-2
339	320	COTIZACION_SOLICITADA_COMPANY	2026-07-01 14:07:54.089792+00	\N	16517406-2
342	321	OPORTUNIDAD_CREADA	2026-07-02 19:18:06.552584+00	\N	16517406-2
343	321	COTIZACION_SOLICITADA_COMPANY	2026-07-02 19:21:12.337708+00	\N	16517406-2
336	319	GANADO	2026-06-30 21:02:11.485824+00	\N	19956311-4
337	316	COTIZACION_SOLICITADA_COMPANY	2026-06-30 21:10:12.48974+00	\N	19956311-4
374	328	COTIZACION_SOLICITADA_COMPANY	2026-07-06 14:42:08.837284+00	\N	28372975-3
377	332	COTIZACION_SOLICITADA_COMPANY	2026-07-06 15:08:32.888742+00	\N	19956311-4
380	333	COTIZACION_SOLICITADA_COMPANY	2026-07-06 16:00:49.096324+00	\N	19956311-4
283	303	COTIZACION_DISPONIBLE	2026-06-23 16:49:25.846958+00	\N	19661132-0
309	312	COTIZACION_DISPONIBLE	2026-06-30 13:55:02.263399+00	\N	19661132-0
314	313	COTIZACION_DISPONIBLE	2026-06-30 16:30:46.708147+00	\N	19661132-0
321	314	COTIZACION_DISPONIBLE	2026-06-21 18:46:04.637878+00	\N	19661132-0
330	319	COTIZACION_DISPONIBLE	2026-06-30 20:35:19.717576+00	\N	19661132-0
340	320	COTIZACION_DISPONIBLE	2026-07-01 15:54:52.894126+00	\N	19661132-0
344	321	COTIZACION_DISPONIBLE	2026-07-02 19:23:47.350691+00	\N	19661132-0
348	322	COTIZACION_DISPONIBLE	2026-07-02 19:42:49.229655+00	\N	19661132-0
365	325	COTIZACION_DISPONIBLE	2026-07-04 21:31:07.583629+00	\N	19661132-0
352	322	COTIZACION_DISPONIBLE	2026-07-03 18:39:34.518295+00	\N	19995707-4
359	323	COTIZACION_DISPONIBLE	2026-07-03 21:39:04.034467+00	\N	19995707-4
375	328	COTIZACION_DISPONIBLE	2026-07-06 14:42:40.097959+00	\N	28372975-3
383	333	POLIZA_REGISTRADA	2026-07-06 16:21:02.884553+00	\N	19956311-4
388	334	ESTUDIO_DISPONIBLE	2026-07-06 16:43:43.973378+00	\N	19661132-0
\.


--
-- Data for Name: lineanegocio; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.lineanegocio (id, nombre, codigo) FROM stdin;
10	Condominio	condominios
12	Líneas Comerciales	lineas_personales
11	Líneas Personales	lineas_comerciales
\.


--
-- Data for Name: permiso; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.permiso (codigo, descripcion) FROM stdin;
ASIGNAR_PROSPECTO	Asignar un prospecto a un ejecutivo comercial o ejecutivo de evaluación de proyectos
REGISTRAR_USUARIOS	Registrar nuevos usuarios
OBTENER_USUARIOS	Obtener datos de los usuarios
EDITAR_PROSPECTO	Editar prospecto
CAMBIAR_ESTADO_PROSPECTO	Actualizar estado de un prospecto
REGISTRAR_PROSPECTO	Registrar prospecto
OBTENER_PROSPECTOS_PROPIOS	Obtener los prospectos registrados por el usuario
OBTENER_PROSPECTOS_TODOS	Obtener todos los prospectos registrados por los usuarios
ASIGNAR_EJECUTIVO_COMERCIAL	Asignar un prospecto a un ejecutivo comercial
ASIGNAR_EJECUTIVO_EVALUACION	Asignar un prospecto a un ejecutivo de evaluación de proyectos
ARMAR_ESTUDIO_COMERCIAL	Permitir al usuario armnar el estudio comercial de un condominio
ACTUALIZAR_DATOS_PROSPECTO	Permite modificar la información de prospectos y clientes asignados al ejecutivo responsable de su gestión.
VER_SOLICITUDES_COTIZACION_PROPIAS	Permite visualizar las solicitudes de cotización de prospectos o clientes bajo la gestión del usuario.
VER_SOLICITUDES_COTIZACION_GLOBAL	Permite visualizar las solicitudes de cotización de todos los prospectos y clientes.
OBTENER_POLIZAS_PROPIAS	Permite visualizar las pólizas de un cliente bajo la gestión del ejecutivo
OBTENER_POLIZAS_TODAS	Permite visualizar las pólizas de todos los clientes
SOLICITAR_COTIZACION	Permite solicitar cotizaciones a evaluación de proyectos para un prospecto o cliente
VER_COTIZACIONES_GLOBAL	Permite visualizar todas las cotizaciones registradas en el sistema, independientemente del cliente o prospecto asociado.
VER_COTIZACIONES_PROPIAS	Permite visualizar únicamente las cotizaciones asociadas a clientes o prospectos cuya gestión está asignada al usuario.
CARGAR_COTIZACIONES	Permite cargar cotizaciones a un cliente o prospecto.
LISTAR_ESTUDIOS_COMERCIALES	Permite visualizar los estudios comerciales de un prospecto o cliente
ADMINISTRAR_PROCESOS_COMERCIALES	Permite consultar y visualizar los reportes gerenciales relacionados con los procesos comerciales.
ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS	Permite administrar oporunidades comerciales de un prospecto o cliente bajo la gestión del ejecutivo.
CARGAR_POLIZAS_PROPIAS	Permite al usuario subir pólizas a un cliente o prospecto bajo su gestión
CARGAR_POLIZAS_GLOBAL	Permite al usuario subir pólizas a cualquier cliente o prospecto
VER_PLAN_PAGO_GLOBAL	Permite consultar el plan de pago de todas las pólizas registradas en el sistema.
VER_PLAN_PAGO_PROPIOS	Permite consultar únicamente el plan de pago de las pólizas asignadas al ejecutivo.
ADMINISTRAR_USUARIOS	Permite crear, editar, activar, desactivar y administrar las cuentas del personal
CREAR_COMUNICADO	Permite al usuario crear un comunicado de gerencia
\.


--
-- Data for Name: permisorol; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.permisorol (codigo_rol, codigo_permiso) FROM stdin;
GERENTE_COMERCIAL	ASIGNAR_PROSPECTO
ASISTENTE_COMERCIAL	REGISTRAR_PROSPECTO
ASISTENTE_COMERCIAL	EDITAR_PROSPECTO
ASISTENTE_COMERCIAL	CAMBIAR_ESTADO_PROSPECTO
GERENTE_GENERAL	ASIGNAR_PROSPECTO
GERENTE_GENERAL	REGISTRAR_USUARIOS
GERENTE_GENERAL	OBTENER_USUARIOS
GERENTE_GENERAL	EDITAR_PROSPECTO
GERENTE_GENERAL	CAMBIAR_ESTADO_PROSPECTO
GERENTE_GENERAL	REGISTRAR_PROSPECTO
GERENTE_GENERAL	OBTENER_PROSPECTOS_TODOS
GERENTE_COMERCIAL	OBTENER_PROSPECTOS_TODOS
GERENTE_OPERACIONES	OBTENER_PROSPECTOS_TODOS
GERENTE_GENERAL	OBTENER_PROSPECTOS_PROPIOS
GERENTE_COMERCIAL	OBTENER_PROSPECTOS_PROPIOS
GERENTE_OPERACIONES	OBTENER_PROSPECTOS_PROPIOS
ASISTENTE_COMERCIAL	OBTENER_PROSPECTOS_PROPIOS
EJECUTIVO_COMERCIAL	OBTENER_PROSPECTOS_PROPIOS
EJECUTIVO_EVALUACION_PROYECTOS	OBTENER_PROSPECTOS_PROPIOS
EJECUTIVO_COMERCIAL	REGISTRAR_PROSPECTO
GERENTE_GENERAL	ASIGNAR_EJECUTIVO_COMERCIAL
GERENTE_GENERAL	ASIGNAR_EJECUTIVO_EVALUACION
GERENTE_COMERCIAL	ASIGNAR_EJECUTIVO_COMERCIAL
GERENTE_COMERCIAL	ASIGNAR_EJECUTIVO_EVALUACION
GERENTE_OPERACIONES	ASIGNAR_EJECUTIVO_COMERCIAL
GERENTE_OPERACIONES	ASIGNAR_EJECUTIVO_EVALUACION
GERENTE_GENERAL	ARMAR_ESTUDIO_COMERCIAL
GERENTE_COMERCIAL	ARMAR_ESTUDIO_COMERCIAL
GERENTE_OPERACIONES	ARMAR_ESTUDIO_COMERCIAL
EJECUTIVO_EVALUACION_PROYECTOS	ARMAR_ESTUDIO_COMERCIAL
EJECUTIVO_COMERCIAL	ACTUALIZAR_DATOS_PROSPECTO
GERENTE_COMERCIAL	ACTUALIZAR_DATOS_PROSPECTO
GERENTE_GENERAL	ACTUALIZAR_DATOS_PROSPECTO
DESARROLLADOR	ASIGNAR_PROSPECTO
DESARROLLADOR	REGISTRAR_USUARIOS
DESARROLLADOR	OBTENER_USUARIOS
DESARROLLADOR	EDITAR_PROSPECTO
DESARROLLADOR	CAMBIAR_ESTADO_PROSPECTO
DESARROLLADOR	REGISTRAR_PROSPECTO
DESARROLLADOR	OBTENER_PROSPECTOS_PROPIOS
DESARROLLADOR	OBTENER_PROSPECTOS_TODOS
DESARROLLADOR	ASIGNAR_EJECUTIVO_COMERCIAL
DESARROLLADOR	ASIGNAR_EJECUTIVO_EVALUACION
DESARROLLADOR	ARMAR_ESTUDIO_COMERCIAL
DESARROLLADOR	ACTUALIZAR_DATOS_PROSPECTO
EJECUTIVO_COMERCIAL	VER_SOLICITUDES_COTIZACION_PROPIAS
EJECUTIVO_EVALUACION_PROYECTOS	VER_SOLICITUDES_COTIZACION_PROPIAS
GERENTE_GENERAL	VER_SOLICITUDES_COTIZACION_GLOBAL
GERENTE_COMERCIAL	VER_SOLICITUDES_COTIZACION_GLOBAL
GERENTE_OPERACIONES	VER_SOLICITUDES_COTIZACION_GLOBAL
GERENTE_GENERAL	OBTENER_POLIZAS_PROPIAS
EJECUTIVO_COMERCIAL	OBTENER_POLIZAS_PROPIAS
EJECUTIVO_EVALUACION_PROYECTOS	OBTENER_POLIZAS_PROPIAS
GERENTE_COMERCIAL	OBTENER_POLIZAS_PROPIAS
GERENTE_OPERACIONES	OBTENER_POLIZAS_PROPIAS
DESARROLLADOR	OBTENER_POLIZAS_PROPIAS
ASISTENTE_COMERCIAL	OBTENER_POLIZAS_PROPIAS
EJECUTIVO_SINIESTROS	OBTENER_POLIZAS_PROPIAS
ASISTENTE_RENOVACION	OBTENER_POLIZAS_PROPIAS
GERENTE_GENERAL	OBTENER_POLIZAS_TODAS
GERENTE_COMERCIAL	OBTENER_POLIZAS_TODAS
GERENTE_OPERACIONES	OBTENER_POLIZAS_TODAS
EJECUTIVO_COMERCIAL	SOLICITAR_COTIZACION
GERENTE_GENERAL	VER_COTIZACIONES_GLOBAL
GERENTE_COMERCIAL	VER_COTIZACIONES_GLOBAL
GERENTE_OPERACIONES	VER_COTIZACIONES_GLOBAL
GERENTE_OPERACIONES	VER_COTIZACIONES_PROPIAS
GERENTE_COMERCIAL	VER_COTIZACIONES_PROPIAS
GERENTE_GENERAL	VER_COTIZACIONES_PROPIAS
ASISTENTE_COMERCIAL	VER_COTIZACIONES_PROPIAS
EJECUTIVO_COMERCIAL	VER_COTIZACIONES_PROPIAS
EJECUTIVO_EVALUACION_PROYECTOS	VER_COTIZACIONES_PROPIAS
ASISTENTE_RENOVACION	VER_COTIZACIONES_PROPIAS
DESARROLLADOR	VER_COTIZACIONES_PROPIAS
EJECUTIVO_EVALUACION_PROYECTOS	CARGAR_COTIZACIONES
ASISTENTE_RENOVACION	CARGAR_COTIZACIONES
EJECUTIVO_RENOVACION_CONDOMINIOS	OBTENER_POLIZAS_PROPIAS
EJECUTIVO_RENOVACION_CONDOMINIOS	VER_COTIZACIONES_PROPIAS
EJECUTIVO_RENOVACION_CONDOMINIOS	CARGAR_COTIZACIONES
EJECUTIVO_RENOVACION_LINEAS_PERSONALES	OBTENER_POLIZAS_PROPIAS
EJECUTIVO_RENOVACION_LINEAS_PERSONALES	VER_COTIZACIONES_PROPIAS
EJECUTIVO_RENOVACION_LINEAS_PERSONALES	CARGAR_COTIZACIONES
EJECUTIVO_SINIESTROS	OBTENER_PROSPECTOS_PROPIOS
ASISTENTE_RENOVACION	OBTENER_PROSPECTOS_PROPIOS
EJECUTIVO_RENOVACION_CONDOMINIOS	OBTENER_PROSPECTOS_PROPIOS
EJECUTIVO_RENOVACION_LINEAS_PERSONALES	OBTENER_PROSPECTOS_PROPIOS
EJECUTIVO_COMERCIAL	LISTAR_ESTUDIOS_COMERCIALES
EJECUTIVO_EVALUACION_PROYECTOS	LISTAR_ESTUDIOS_COMERCIALES
GERENTE_COMERCIAL	LISTAR_ESTUDIOS_COMERCIALES
GERENTE_GENERAL	LISTAR_ESTUDIOS_COMERCIALES
GERENTE_OPERACIONES	LISTAR_ESTUDIOS_COMERCIALES
GERENTE_GENERAL	ADMINISTRAR_PROCESOS_COMERCIALES
GERENTE_COMERCIAL	ADMINISTRAR_PROCESOS_COMERCIALES
GERENTE_OPERACIONES	ADMINISTRAR_PROCESOS_COMERCIALES
EJECUTIVO_COMERCIAL	ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS
EJECUTIVO_EVALUACION_PROYECTOS	ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS
GERENTE_GENERAL	VER_SOLICITUDES_COTIZACION_PROPIAS
GERENTE_GENERAL	SOLICITAR_COTIZACION
GERENTE_GENERAL	CARGAR_COTIZACIONES
GERENTE_GENERAL	ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS
GERENTE_GENERAL	CARGAR_POLIZAS_PROPIAS
GERENTE_GENERAL	CARGAR_POLIZAS_GLOBAL
GERENTE_COMERCIAL	CARGAR_POLIZAS_PROPIAS
GERENTE_COMERCIAL	CARGAR_POLIZAS_GLOBAL
GERENTE_OPERACIONES	CARGAR_POLIZAS_PROPIAS
GERENTE_OPERACIONES	CARGAR_POLIZAS_GLOBAL
EJECUTIVO_COMERCIAL	CARGAR_POLIZAS_PROPIAS
EJECUTIVO_RENOVACION_CONDOMINIOS	CARGAR_POLIZAS_PROPIAS
EJECUTIVO_RENOVACION_LINEAS_PERSONALES	CARGAR_POLIZAS_PROPIAS
EJECUTIVO_COBRANZA_CONDOMINIOS	OBTENER_POLIZAS_PROPIAS
EJECUTIVO_COBRANZA_CONDOMINIOS	OBTENER_PROSPECTOS_PROPIOS
GERENTE_GENERAL	VER_PLAN_PAGO_GLOBAL
GERENTE_COMERCIAL	VER_PLAN_PAGO_GLOBAL
GERENTE_OPERACIONES	VER_PLAN_PAGO_GLOBAL
GERENTE_GENERAL	VER_PLAN_PAGO_PROPIOS
GERENTE_COMERCIAL	VER_PLAN_PAGO_PROPIOS
GERENTE_OPERACIONES	VER_PLAN_PAGO_PROPIOS
EJECUTIVO_COBRANZA_CONDOMINIOS	VER_PLAN_PAGO_PROPIOS
EJECUTIVO_COBRANZA_LINEAS_PERSONALES	VER_PLAN_PAGO_PROPIOS
EJECUTIVO_COMERCIAL	VER_PLAN_PAGO_PROPIOS
EJECUTIVO_COMERCIAL	ARMAR_ESTUDIO_COMERCIAL
EJECUTIVO_COMERCIAL	CARGAR_COTIZACIONES
GERENTE_GENERAL	ADMINISTRAR_USUARIOS
GERENTE_GENERAL	CREAR_COMUNICADO
GERENTE_COMERCIAL	CREAR_COMUNICADO
GERENTE_OPERACIONES	CREAR_COMUNICADO
EJECUTIVO_EVALUACION_PROYECTOS	ACTUALIZAR_DATOS_PROSPECTO
EJECUTIVO_EVALUACION_PROYECTOS	SOLICITAR_COTIZACION
GERENTE_COMERCIAL	REGISTRAR_USUARIOS
GERENTE_COMERCIAL	OBTENER_USUARIOS
GERENTE_COMERCIAL	EDITAR_PROSPECTO
GERENTE_COMERCIAL	CAMBIAR_ESTADO_PROSPECTO
GERENTE_COMERCIAL	REGISTRAR_PROSPECTO
GERENTE_COMERCIAL	VER_SOLICITUDES_COTIZACION_PROPIAS
GERENTE_COMERCIAL	SOLICITAR_COTIZACION
GERENTE_COMERCIAL	CARGAR_COTIZACIONES
GERENTE_COMERCIAL	ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS
GERENTE_COMERCIAL	ADMINISTRAR_USUARIOS
GERENTE_OPERACIONES	ASIGNAR_PROSPECTO
GERENTE_OPERACIONES	REGISTRAR_USUARIOS
GERENTE_OPERACIONES	OBTENER_USUARIOS
GERENTE_OPERACIONES	EDITAR_PROSPECTO
GERENTE_OPERACIONES	CAMBIAR_ESTADO_PROSPECTO
GERENTE_OPERACIONES	REGISTRAR_PROSPECTO
GERENTE_OPERACIONES	ACTUALIZAR_DATOS_PROSPECTO
GERENTE_OPERACIONES	VER_SOLICITUDES_COTIZACION_PROPIAS
GERENTE_OPERACIONES	SOLICITAR_COTIZACION
GERENTE_OPERACIONES	CARGAR_COTIZACIONES
GERENTE_OPERACIONES	ADMINISTRAR_PROCESOS_COMERCIALES_PROPIOS
GERENTE_OPERACIONES	ADMINISTRAR_USUARIOS
\.


--
-- Data for Name: planificacionprospecto; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.planificacionprospecto (id_prospecto, id_company, prima_vigente, termino_vigencia, monto_asegurado_vigente, fecha_envio_cotizacion) FROM stdin;
7	3	300	\N	319560	2026-07-03 18:00:51.02949+00
115	3	300	\N	330000	\N
\.


--
-- Data for Name: planpago; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.planpago (id, numero_poliza) FROM stdin;
2	98797987
3	6549876541
4	987451254
5	522222222
6	51248787
7	11212121
\.


--
-- Data for Name: poliza; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.poliza (numero_poliza, id_cliente, prima_neta, comision_corredora_pct, fecha_emision, inicio_vigencia, fin_vigencia, id_company, id_proceso_comercial, cancelada, renovacion_cotizada, tipo) FROM stdin;
100	47	10.67	0.14	2026-03-01 12:00:00+00	\N	\N	\N	118	f	f	nueva
101	48	11.06	0.14	2026-03-01 12:00:00+00	\N	\N	\N	119	f	f	nueva
102	49	11.13	0.17	2026-03-01 12:00:00+00	\N	\N	\N	120	f	f	nueva
103	50	513.15	0.138	2026-03-01 12:00:00+00	\N	\N	\N	121	f	f	nueva
104	51	17	0.13	2026-03-01 12:00:00+00	\N	\N	\N	122	f	f	nueva
105	52	124	0.15	2026-03-01 12:00:00+00	\N	\N	\N	123	f	f	nueva
106	53	31.69	0.15	2026-03-01 12:00:00+00	\N	\N	\N	124	f	f	nueva
108	55	82.9	0.14	2026-03-01 12:00:00+00	\N	\N	\N	126	f	f	nueva
109	56	7.55	0.25	2026-03-01 12:00:00+00	\N	\N	\N	127	f	f	nueva
107	54	93.1	0.15	2026-03-01 12:00:00+00	\N	\N	\N	125	f	f	nueva
1010	57	349.78	0.17	2026-05-01 12:00:00+00	\N	\N	12	128	f	f	nueva
1012	58	155	0.13	2026-05-01 12:00:00+00	\N	\N	4	130	f	f	nueva
1013	59	364.8	0.13	2026-05-01 12:00:00+00	\N	\N	4	131	f	f	nueva
1014	60	175	0.13	2026-05-01 12:00:00+00	\N	\N	4	132	f	f	nueva
1015	61	43.8	0.15	2026-05-01 12:00:00+00	\N	\N	10	133	f	f	nueva
1016	62	74.51	0.15	2026-05-01 12:00:00+00	\N	\N	10	134	f	f	nueva
1019	65	16.3	0.15	2026-05-01 12:00:00+00	\N	\N	12	137	f	f	nueva
1020	66	3.81	0.14	2026-05-01 12:00:00+00	\N	\N	15	138	f	f	nueva
1021	67	6.07	0.14	2026-05-01 12:00:00+00	\N	\N	4	139	f	f	nueva
1022	68	126.6	0.15	2026-05-01 12:00:00+00	\N	\N	10	140	f	f	nueva
1023	69	4.07	0.20709999	2026-05-01 12:00:00+00	\N	\N	12	141	f	f	nueva
1024	70	378.12	0.15	2026-05-01 12:00:00+00	\N	\N	4	142	f	f	nueva
1025	62	74.51	0.15	2026-05-01 12:00:00+00	\N	\N	10	143	f	f	nueva
1026	71	11.59	0.17	2026-05-01 12:00:00+00	\N	\N	12	144	f	f	nueva
1027	60	94.39	0.13	2026-05-01 12:00:00+00	\N	\N	4	145	f	f	nueva
1028	72	9.1	0.17	2026-05-01 12:00:00+00	\N	\N	7	146	f	f	nueva
1029	73	11.4	0.17	2026-05-01 12:00:00+00	\N	\N	12	147	f	f	nueva
1031	75	1	0.1	2026-05-01 12:00:00+00	\N	\N	4	149	f	f	nueva
1032	74	1	0.1	2026-05-01 12:00:00+00	\N	\N	4	150	f	f	nueva
1033	76	1	0.1	2026-05-01 12:00:00+00	\N	\N	4	151	f	f	nueva
1034	77	1	0.1	2026-05-01 12:00:00+00	\N	\N	4	152	f	f	nueva
1035	78	1	0.1	2026-05-01 12:00:00+00	\N	\N	4	153	f	f	nueva
1036	79	16	0.13	2026-05-01 12:00:00+00	\N	\N	13	154	f	f	nueva
1037	80	10	0.15	2026-05-01 12:00:00+00	\N	\N	7	155	f	f	nueva
1038	81	8.4	0.15	2026-05-01 12:00:00+00	\N	\N	7	156	f	f	nueva
1039	82	15.41	0.17	2026-05-01 12:00:00+00	\N	\N	12	157	f	f	nueva
1040	83	70.7	0.13	2026-05-01 12:00:00+00	\N	\N	4	158	f	f	nueva
1041	84	1064.53	0.13	2026-05-01 12:00:00+00	\N	\N	4	159	f	f	nueva
1042	85	233.25	0.15	2026-05-01 12:00:00+00	\N	\N	10	160	f	f	nueva
1043	86	211.76	0.15	2026-05-01 12:00:00+00	\N	\N	10	161	f	f	nueva
1044	87	825.09	0.13	2026-05-01 12:00:00+00	\N	\N	10	162	f	f	nueva
1045	88	25.9	0.13	2026-05-01 12:00:00+00	\N	\N	4	163	f	f	nueva
1046	89	330	0.1	2026-05-01 12:00:00+00	\N	\N	15	164	f	f	nueva
1047	89	132.63	0.1	2026-05-01 12:00:00+00	\N	\N	15	165	f	f	nueva
1048	90	12.25	0.14	2026-05-01 12:00:00+00	\N	\N	9	166	f	f	nueva
1018	64	219.3	0.15	2026-05-01 12:00:00+00	\N	\N	10	136	f	f	renovacion
6549876541	95	1500	0.13	2026-06-30 00:00:00+00	2026-07-01 00:00:00+00	2027-07-01 00:00:00+00	8	312	f	f	nueva
987451254	96	1360	0.145	2026-06-30 00:00:00+00	2026-07-01 00:00:00+00	2027-07-01 00:00:00+00	6	313	f	f	nueva
15245870	93	150	0.15	2026-06-22 16:15:00+00	2026-06-24 00:00:00+00	2027-06-24 00:00:00+00	4	295	f	f	nueva
1049	91	111.38	0.15	2026-05-01 12:00:00+00	\N	\N	10	167	f	f	nueva
1017	63	203.99	0.13	2026-05-01 12:00:00+00	\N	\N	4	135	f	t	nueva
1050	92	339.21	0.1468	2026-05-01 12:00:00+00	\N	\N	1	168	f	f	nueva
1051	84	5	0.15	2026-05-01 12:00:00+00	\N	\N	4	169	f	f	nueva
1052	58	3	0.15	2026-05-01 12:00:00+00	\N	\N	4	170	f	f	nueva
1053	87	15	0.12	2026-05-01 12:00:00+00	\N	\N	10	171	f	f	nueva
1054	92	8	0.1	2026-05-01 12:00:00+00	\N	\N	1	172	f	f	nueva
1030	74	7.06	0.15	2026-05-01 12:00:00+00	\N	\N	7	148	f	f	nueva
1011	58	155	0.13	2026-05-01 12:00:00+00	\N	\N	4	129	f	f	nueva
15228496	94	2000	0.14	2026-06-23 00:00:00+00	2026-06-29 00:00:00+00	2027-06-29 00:00:00+00	7	6	f	f	nueva
11111111111	94	3500	0.135	2026-06-22 00:00:00+00	2026-06-23 00:00:00+00	2027-06-23 00:00:00+00	4	296	f	f	nueva
14203568	94	20	0.1	2026-06-23 00:00:00+00	2026-07-01 00:00:00+00	2027-08-01 00:00:00+00	1	303	f	f	nueva
251687517	59	200	0.13	2026-06-23 00:00:00+00	2026-06-29 00:00:00+00	2027-06-29 00:00:00+00	13	298	f	f	nueva
6695874512	57	200	0.123	2026-06-25 00:00:00+00	2026-07-01 00:00:00+00	2027-07-01 00:00:00+00	15	300	f	f	renovacion
556598541	52	1200	0.15	2026-06-24 00:00:00+00	2026-06-24 00:00:00+00	2027-06-24 00:00:00+00	9	304	f	f	renovacion
99656487	78	30	0.13	2026-06-25 00:00:00+00	2026-06-26 00:00:00+00	2027-06-26 00:00:00+00	15	305	f	f	nueva
85848785	75	15	0.1	2026-06-25 00:00:00+00	2026-07-01 00:00:00+00	2027-07-01 00:00:00+00	6	306	f	f	nueva
321321321	75	10	0.12	2026-06-23 00:00:00+00	2026-06-24 00:00:00+00	2027-06-24 00:00:00+00	12	307	f	f	nueva
65465654	53	50	0.13	2026-06-25 00:00:00+00	2026-06-26 00:00:00+00	2027-06-26 00:00:00+00	13	308	f	f	nueva
98797987	53	1200	0.13	2025-06-01 00:00:00+00	2025-06-03 00:00:00+00	2026-06-03 00:00:00+00	8	310	f	f	nueva
98754	53	1200	0.13	2026-06-01 00:00:00+00	2026-06-03 00:00:00+00	2027-06-03 00:00:00+00	13	311	f	f	nueva
522222222	97	520.91	0.17	2026-06-20 00:00:00+00	2026-06-20 00:00:00+00	2027-06-20 00:00:00+00	9	319	f	f	nueva
51248787	96	1200	0.13	2026-07-03 00:00:00+00	2026-07-03 00:00:00+00	2027-07-03 00:00:00+00	10	314	f	f	nueva
11212121	98	30	0.126	2026-07-03 00:00:00+00	2026-07-06 00:00:00+00	2027-07-06 00:00:00+00	4	323	f	f	nueva
654654318	96	250	0.14	2026-07-01 00:00:00+00	2026-07-01 00:00:00+00	2027-07-01 00:00:00+00	9	324	f	f	renovacion
251485124	97	650	0.15	2026-07-06 00:00:00+00	2026-07-08 00:00:00+00	2027-07-08 00:00:00+00	8	333	f	f	nueva
\.


--
-- Data for Name: procesocomercial; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.procesocomercial (id, id_prospecto, rut_ej_comercial, id_producto, cerrado, codigo_estado_actual, renovacion, rut_ej_renovacion, rut_as_renovacion, motivo_cierre, monto_asegurado_actual, rut_ej_evaluacion) FROM stdin;
320	115	19956311-4	1	f	ESTUDIO_DISPONIBLE	f	\N	\N	\N	\N	19956311-4
318	115	19956311-4	25	f	OPORTUNIDAD_CREADA	f	\N	\N	\N	\N	19956311-4
307	89	19956311-4	9	t	GANADO	f	\N	\N	\N	\N	\N
315	90	19956311-4	6	t	PERDIDO	f	\N	\N	\N	\N	\N
331	123	28372975-3	9	f	OPORTUNIDAD_CREADA	f	\N	\N	\N	\N	\N
328	123	28372975-3	5	f	COTIZACION_DISPONIBLE	f	\N	\N	\N	\N	\N
323	118	19995707-4	25	t	GANADO	f	\N	\N	\N	\N	\N
137	79	28372975-3	24	t	GANADO	f	\N	\N	\N	\N	\N
138	80	28372975-3	24	t	GANADO	f	\N	\N	\N	\N	\N
139	81	28372975-3	24	t	GANADO	f	\N	\N	\N	\N	\N
321	117	19661132-0	1	f	ESTUDIO_DISPONIBLE	f	\N	\N	\N	\N	\N
127	70	21036887-1	24	t	GANADO	f	\N	\N	\N	\N	\N
300	71	19995707-4	25	t	GANADO	f	\N	\N	\N	\N	\N
325	118	19995707-4	2	f	ESTUDIO_DISPONIBLE	f	\N	\N	\N	\N	\N
128	71	19995707-4	24	t	GANADO	f	\N	\N	\N	\N	\N
118	61	19995707-4	24	t	GANADO	f	\N	\N	\N	\N	\N
119	62	19995707-4	24	t	GANADO	f	\N	\N	\N	\N	\N
120	63	19995707-4	24	t	GANADO	f	\N	\N	\N	\N	\N
121	64	19995707-4	24	t	GANADO	f	\N	\N	\N	\N	\N
129	72	19995707-4	24	t	GANADO	f	\N	\N	\N	\N	\N
131	73	19995707-4	24	t	GANADO	f	\N	\N	\N	\N	\N
140	82	21036887-3	24	t	GANADO	f	\N	\N	\N	\N	\N
141	83	21036887-3	24	t	GANADO	f	\N	\N	\N	\N	\N
142	84	21036887-3	24	t	GANADO	f	\N	\N	\N	\N	\N
314	113	19995707-4	2	t	GANADO	f	\N	\N	\N	\N	\N
313	113	19995707-4	1	t	GANADO	f	\N	\N	\N	\N	\N
6	7	16517406-2	1	t	GANADO	f	\N	\N	\N	\N	\N
299	7	16517406-2	4	t	PERDIDO	f	\N	\N	\N	\N	\N
301	68	16517406-2	26	t	PERDIDO	f	\N	\N	\N	\N	\N
304	66	16517406-2	26	t	GANADO	f	\N	\N	\N	\N	\N
308	67	16517406-2	4	t	GANADO	f	\N	\N	\N	\N	\N
311	67	16517406-2	2	t	GANADO	f	\N	\N	\N	\N	\N
312	112	16517406-2	2	t	GANADO	f	\N	\N	\N	\N	\N
122	65	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
123	66	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
124	67	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
125	68	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
126	69	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
130	72	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
132	74	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
133	75	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
134	76	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
135	77	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
136	78	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
326	118	19995707-4	4	f	COTIZACION_SOLICITADA_COMPANY	f	\N	\N	\N	\N	\N
322	118	19995707-4	1	f	ESTUDIO_DISPONIBLE	f	\N	\N	\N	\N	\N
324	113	19995707-4	2	f	OPORTUNIDAD_CREADA	f	\N	\N	\N	\N	\N
309	67	16517406-2	4	t	PERDIDO	f	\N	\N	\N	\N	\N
143	76	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
144	85	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
145	74	16517406-2	24	t	GANADO	f	\N	\N	\N	\N	\N
305	92	19956311-4	6	t	GANADO	f	\N	\N	\N	\N	\N
319	115	19956311-4	1	t	GANADO	f	\N	\N	\N	\N	\N
146	86	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
147	87	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
148	88	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
149	89	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
150	88	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
151	90	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
152	91	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
153	92	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
154	93	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
329	123	28372975-3	6	f	OPORTUNIDAD_CREADA	f	\N	\N	\N	\N	\N
316	115	19956311-4	26	f	COTIZACION_SOLICITADA_COMPANY	f	\N	\N	\N	\N	19956311-4
332	81	19956311-4	6	f	COTIZACION_DISPONIBLE	f	\N	\N	\N	\N	\N
333	115	19956311-4	2	f	COTIZACION_DISPONIBLE	f	\N	\N	\N	\N	\N
334	78	19956311-4	2	f	PROPUESTA_ACEPTADA	f	\N	\N	\N	\N	\N
164	103	15634751-5	24	t	GANADO	f	\N	\N	\N	\N	\N
165	103	15634751-5	24	t	GANADO	f	\N	\N	\N	\N	\N
298	73	19995707-4	26	t	GANADO	f	\N	\N	\N	\N	\N
327	118	19995707-4	26	f	OPORTUNIDAD_CREADA	f	\N	\N	\N	\N	\N
297	7	16517406-2	25	t	GANADO	f	\N	\N	El cliente envió la aceptación	\N	\N
293	8	16517406-2	1	t	GANADO	f	\N	\N	\N	\N	\N
302	68	16517406-2	25	t	PERDIDO	f	\N	\N	\N	\N	\N
295	8	16517406-2	2	t	GANADO	f	\N	\N	\N	\N	\N
296	7	16517406-2	4	t	GANADO	f	\N	\N	\N	\N	\N
303	7	16517406-2	26	t	GANADO	f	\N	\N	\N	\N	\N
310	67	16517406-2	2	t	GANADO	f	\N	\N	\N	\N	\N
155	94	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
156	95	19956311-4	24	t	GANADO	f	\N	\N	\N	\N	\N
306	89	19956311-4	7	t	GANADO	f	\N	\N	\N	\N	\N
330	123	28372975-3	7	f	OPORTUNIDAD_CREADA	f	\N	\N	\N	\N	\N
157	96	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
158	97	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
159	98	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
160	99	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
161	100	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
162	101	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
163	102	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
166	104	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
167	105	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
168	106	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
169	98	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
170	72	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
171	101	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
172	106	12220101-5	24	t	GANADO	f	\N	\N	\N	\N	\N
317	115	19956311-4	4	f	OPORTUNIDAD_CREADA	f	\N	\N	\N	\N	19956311-4
\.


--
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.producto (id, nombre, id_linea_negocio, codigo) FROM stdin;
10	Incendio	12	\N
11	Responsabilidad Civil	12	\N
12	Accidentes Personales	12	\N
13	Vehículos Pesados	12	\N
14	Transporte Terrestre	12	\N
15	Todo Riesgo Construcción	12	\N
16	Garantía	12	\N
17	Equipo Móvil Contratista	12	\N
18	Vida Conductor	12	\N
19	Asiento Pasajero	12	\N
20	Flotas	12	\N
21	Responsabilidad Civil Evento	12	\N
22	Complementario de Salud Colectivo	12	\N
23	Catastrófico Colectivo	12	\N
2	Unidades	10	unidades
4	Vida Guardia	10	vida_guardia
24	Sismo + Incendio	10	sismo_incendio
1	Espacios Comunes	10	espacios_comunes
25	Accidentes personales	10	accidentes_personales
26	Responsabilidad Civil Condominio	10	rc_condominio
6	Hogar	11	hogar
5	Vehículo	11	vehiculos
7	Complementario de Salud Individual	11	salud_complementario
9	Seguro Mascota	11	mascotas
8	Catastrófico Individual	11	catastrofico_individual
3	D&O	10	rc_directores_y_administradores
\.


--
-- Data for Name: prospecto; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.prospecto (id, rut_riesgo, nombre_riesgo, telefono_contacto, correo_contacto, direccion, observaciones, id_linea_negocio, rut_registrado_por, created_at, updated_at, region, comuna, rut_ej_comercial_asignado, informacion_completa, rut_ej_evaluacion_asignado) FROM stdin;
120	\N	asasd	\N	\N	\N	\N	11	20036887-8	2026-07-06 14:32:56.043687+00	2026-07-06 14:54:07.121582+00	Región de Antofagasta	Sierra Gorda	19956311-4	f	\N
64	53311726-0	Condominio Infinity Nativa	\N	\N	\N	\N	10	19995707-4	2026-06-05 19:50:22.001933+00	2026-07-06 14:48:46.798781+00	\N	\N	19995707-4	f	19661132-0
61	20025757-k	Sofia Llanos	\N	\N	\N	\N	11	19995707-4	2026-06-05 19:50:21.801932+00	2026-07-06 14:48:46.798781+00	\N	\N	19995707-4	f	19661132-0
62	20225549-3	Paulina Lobos	\N	\N	\N	\N	11	19995707-4	2026-06-05 19:50:21.872036+00	2026-07-06 14:48:46.798781+00	\N	\N	19995707-4	f	19661132-0
63	11823433-2	Alejandra Rojas	\N	\N	\N	\N	11	19995707-4	2026-06-05 19:50:21.9404+00	2026-07-06 14:48:46.798781+00	\N	\N	19995707-4	f	19661132-0
67	76166974-5	Bemec Comunicaciones	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.18105+00	2026-07-06 15:07:40.769642+00	\N	\N	16517406-2	f	\N
65	65021829-9	Condominio Las Nieves	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.061832+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
66	53333599-3	Casonas IV	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.118831+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
68	53322748-1	Condominio El Canelo	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.244684+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
121	\N	Miguel Pérez	\N	\N	\N	\N	11	20036887-8	2026-07-06 14:37:31.245802+00	2026-07-06 14:37:31.245802+00	\N	\N	20036887-8	f	\N
71	53332125-9	EDIFICIO TORRE BERLIN	\N	\N	\N	\N	10	19995707-4	2026-06-05 19:50:22.421299+00	2026-07-06 14:48:46.798781+00	\N	\N	19995707-4	f	19661132-0
73	53324455-6	CONDOMINIO LEGADO	\N	\N	\N	\N	10	19995707-4	2026-06-05 19:50:22.597532+00	2026-07-06 14:48:46.798781+00	\N	\N	19995707-4	f	19661132-0
69	65093752-k	CONDOMINIO LOS TEMPLARIOS	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.303156+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
74	53303888-3	COMUNIDAD EDIFICIO FUSION (EECC)	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.667412+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
75	53327165-0	EDIFICIO VEINTIUNO DE MAYO	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.729036+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
76	53327164-2	CONDOMINIO MERCED 438	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.817375+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
77	53318226-7	COMUNIDAD CUMBRES DE HUECHURABA	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.887367+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
70	76945998-7	FCV SPA	\N	\N	\N	\N	10	21036887-1	2026-06-05 19:50:22.363098+00	2026-07-06 14:24:25.245131+00	\N	\N	21036887-1	f	19661132-0
122	\N	erererer	\N	\N	\N	\N	11	20036887-8	2026-07-06 14:38:01.278234+00	2026-07-06 14:38:01.278234+00	\N	\N	20036887-8	f	\N
72	65191061-7	CONDOMINIO EDIFICIO BARTOLO SOTO 2	\N	\N	\N	\N	10	19995707-4	2026-06-05 19:50:22.479882+00	2026-07-06 14:48:46.798781+00	\N	\N	19995707-4	f	19661132-0
103	56066090-1	EDIFICIO CONDOMINIO BOSQUE DE PATAGUAS	\N	\N	\N	\N	10	15634751-5	2026-06-05 19:50:24.684967+00	2026-07-06 14:50:59.915647+00	\N	\N	15634751-5	f	19661132-0
7		Vive San Francisco	89826862	Comitecitycentro2@gmail.com	Santo Domingo 1161		10	20036887-8	2026-05-27 13:30:26.664163+00	2026-07-06 14:49:26.579255+00	Región Metropolitana de Santiago	Santiago	16517406-2	f	19661132-0
8	53.313.035-6	Edificio Geocentro Santa Rosa II	94339151	contacto@admiv.cl	Santa Rosa 265		10	20036887-8	2026-05-27 13:30:26.664163+00	2026-07-06 14:49:26.579255+00	Región Metropolitana de Santiago	Puente Alto	16517406-2	t	19661132-0
107	10459880-3	Edificio Jorge Prueba	94339151	contacto@admiv.cl	Santa Rosa 265		10	16517406-2	2026-06-17 19:41:09.907589+00	2026-07-06 14:49:26.579255+00	Región Metropolitana de Santiago	Santiago	16517406-2	f	19661132-0
108	10754271-k	Prueba 2	\N	\N	\N	\N	10	16517406-2	2026-06-18 00:00:57.72634+00	2026-07-06 14:49:26.579255+00	Región de Coquimbo	Coquimbo	16517406-2	f	19661132-0
111	24156598-k	asd	\N	\N	\N	\N	10	16517406-2	2026-06-18 17:11:38.398678+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
78	65244238-2	CONDOMINIO LOMAS DE BORGOÑO	\N	\N	\N	\N	10	16517406-2	2026-06-05 19:50:22.946092+00	2026-07-06 16:37:48.22745+00	\N	\N	19956311-4	f	19661132-0
82	53336270-2	EDIFICIO BOLDO PARQUE EL RODEO	\N	\N	\N	\N	10	21036887-3	2026-06-05 19:50:23.203921+00	2026-07-06 14:24:25.245131+00	\N	\N	21036887-3	f	19661132-0
84	53314170-6	CONJUNTO HABITACIONAL CASCADAS DEL SUR EDIFICIO TRANCURA	\N	\N	\N	\N	10	21036887-3	2026-06-05 19:50:23.321114+00	2026-07-06 14:24:25.245131+00	\N	\N	21036887-3	f	19661132-0
97	53300223-4	COMUNIDAD EDIFICIO BUENA VISTA	\N	\N	\N	\N	10	12220101-5	2026-06-05 19:50:24.306531+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
98	65137948-2	CONDOMINIO ALTO HACIENDA	\N	\N	\N	\N	10	12220101-5	2026-06-05 19:50:24.374507+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
99	65273079-5	EDIFICIO RIBERA KAUKARI	\N	\N	\N	\N	10	12220101-5	2026-06-05 19:50:24.436503+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
100	65272325-k	CONDOMINIO ALTAMIRA V	\N	\N	\N	\N	10	12220101-5	2026-06-05 19:50:24.498741+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
101	53323974-9	CONDOMINIO AQUA	\N	\N	\N	\N	10	12220101-5	2026-06-05 19:50:24.567436+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
102	53327801-9	CONDOMINIO SAN MARCOS	\N	\N	\N	\N	10	12220101-5	2026-06-05 19:50:24.625263+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
104	53325187-0	COMUNIDAD EDIFICIO LOFT PLAZA YUNGAY	\N	\N	\N	\N	10	12220101-5	2026-06-05 19:50:24.796341+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
114	65216482-k	Edificio Paseo Balmaceda	\N	\N	\N	\N	10	20036887-8	2026-06-30 19:37:45.318798+00	2026-06-30 19:38:00.271845+00	\N	\N	21036887-1	f	\N
123	\N	ccfv	\N	\N	\N	\N	11	20036887-8	2026-07-06 14:39:40.680549+00	2026-07-06 14:50:35.19999+00	\N	\N	28372975-3	f	28372975-3
113	70521684-3	Edificio para pruebas	\N	\N	\N	\N	10	20036887-8	2026-06-30 16:18:51.228679+00	2026-07-06 14:48:46.798781+00	Región de Atacama	Vallenar	19995707-4	f	19995707-4
118	65191853-7	Condominio Parque Mackenna	\N	condominioparquemackenna@gmail.com	Vicuña Mackenna 4192	\N	10	20036887-8	2026-07-02 19:33:50.869504+00	2026-07-06 14:48:46.798781+00	Región Metropolitana de Santiago	Macul	19995707-4	t	19995707-4
116	32659217-k	Prueba 11	\N	\N	\N	\N	10	20036887-8	2026-07-01 14:18:26.013561+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	\N
85	12055505-7	Katherine Avila Magna	\N	\N	\N	\N	11	16517406-2	2026-06-05 19:50:23.426277+00	2026-07-06 14:49:26.579255+00	\N	\N	16517406-2	f	19661132-0
79	25678375-4	Melina Noto	\N	\N	\N	\N	11	28372975-3	2026-06-05 19:50:23.004776+00	2026-07-06 14:50:35.19999+00	\N	\N	28372975-3	f	19661132-0
80	17919136-9	Francisca Gallardo	\N	\N	\N	\N	11	28372975-3	2026-06-05 19:50:23.067161+00	2026-07-06 14:50:35.19999+00	\N	\N	28372975-3	f	19661132-0
86	13031649-2	ERNESTO FABIAN LAGOS QUEZADA	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:23.545207+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
87	17620248-3	YENNIFER NICOLLE TAPIA CORTES	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:23.617735+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
88	17633904-7	SEBASTIAN FELIPE ARAYA GONZALEZ	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:23.677382+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
89	17356116-4	VICENTE DEL VILLAR RAMIREZ	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:23.745515+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
81	19604311-k	Catalina Castel Blanco	\N	\N	\N	\N	11	28372975-3	2026-06-05 19:50:23.138499+00	2026-07-06 15:08:14.565774+00	Región del Biobío	Cabrero	19956311-4	f	19956311-4
93	16957251-8	LORETO ACEVEDO 	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:24.067981+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
90	17266249-8	DIEGO PABLO GUZMAN SANCHEZ 	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:23.869107+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
91	17601797-k	PABLO MAXIMILIANO ITURRIAGA WILDER	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:23.931809+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
92	17660006-3	DIEGO ANDRES DIAZ CANO 	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:23.999817+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
94	15316146-1	MARIBEL VALENCIA	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:24.127972+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
115	207406988	Prueba 10	\N	Comitecitycentro2@gmail.com		mmmmmmmmmmmmm	10	19956311-4	2026-06-30 20:21:16.683031+00	2026-07-06 16:04:30.040658+00	Región de Los Lagos	Dalcahue	19956311-4	f	19956311-4
105	56026300-7	COMUNIDAD EDIFICIO PONTEVEDRA	\N	\N	\N	\N	10	12220101-5	2026-06-05 19:50:24.864615+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
83	5322110-6	Luis Urrutia Martinez	\N	\N	\N	\N	11	21036887-3	2026-06-05 19:50:23.26201+00	2026-07-06 14:24:25.245131+00	\N	\N	21036887-3	f	19661132-0
106	65235991-4	CONDOMINIO AIRES DEL LIMARI	\N	\N	\N	\N	10	12220101-5	2026-06-05 19:50:24.926916+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
96	11806243-4	LORENA DEL PILAR ARAYA TRONCOSO	\N	\N	\N	\N	11	12220101-5	2026-06-05 19:50:24.24581+00	2026-07-06 14:24:25.245131+00	\N	\N	12220101-5	f	19661132-0
117	85164215-3	Edificio Prueba 12	\N	a@a	asd	\N	10	20036887-8	2026-07-02 19:15:46.214315+00	2026-07-06 14:24:25.245131+00	Región del Biobío	Coronel	19661132-0	f	19661132-0
112	17617859-0	Condominio Prueba 7	\N	a@a	prueba	\N	10	20036887-8	2026-06-30 13:33:51.618872+00	2026-07-06 14:49:26.579255+00	Región de Coquimbo	La Serena	16517406-2	f	19661132-0
95	10231700-9	IVETTE VALDEBENITO	\N	\N	\N	\N	11	19956311-4	2026-06-05 19:50:24.18681+00	2026-07-06 14:49:55.353362+00	\N	\N	19956311-4	f	19661132-0
\.


--
-- Data for Name: prospectocondominio; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.prospectocondominio (id, tiene_locales_comerciales, uso_del_condominio, numero_pisos, numero_torres, cantidad_departamentos, cantidad_subterraneos, tiene_piscina, year_construccion, metros_cuadrados, updated_at, id_administrador, materialidad, clasificacion_preliminar_incendio, procesos_productivos, ubicacion_piscina, tiene_alarma_incendio, tiene_sprinklers, uf_por_metro_cuadrado, porcentaje_depreciacion, porcentaje_espacios_comunes, created_at) FROM stdin;
78	\N	\N	\N	\N	750	\N	\N	2025	50000	2026-06-05 19:50:22.946092+00	1	\N	\N	\N	\N	\N	\N	28	0	0.7	2026-06-08 19:36:01.713236+00
7	f	habitacional	6	4	200	0	\N	2020	25715.68	2026-05-27 13:37:12.706797+00	1	hormigon_armado	incombustible	t		t	t	30	0.15	0.7	2026-06-08 19:36:01.713236+00
112	t	mixto	18	3	450	0	t	2020	20000	2026-06-30 13:33:51.618872+00	1	hormigon_armado	incombustible	f	primer_piso	f	f	25	0.15	0.7	2026-06-30 13:33:51.618872+00
61	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:21.801932+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
62	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:21.872036+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
63	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:21.9404+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
64	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.001933+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
65	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.061832+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
66	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.118831+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
67	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.18105+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
68	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.244684+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
69	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.303156+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
70	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.363098+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
71	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.421299+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
73	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.597532+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
74	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.667412+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
75	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.729036+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
76	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.817375+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
77	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.887367+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
79	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.004776+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
80	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.067161+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
81	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.138499+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
82	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.203921+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
83	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.26201+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
84	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.321114+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
85	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.426277+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
86	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.545207+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
87	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.617735+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
88	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.677382+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
89	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.745515+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
90	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.869107+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
91	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.931809+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
92	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:23.999817+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
93	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.067981+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
94	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.127972+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
95	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.18681+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
96	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.24581+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
97	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.306531+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
98	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.374507+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
99	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.436503+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
100	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.498741+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
101	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.567436+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
102	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.625263+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
103	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.684967+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
104	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.796341+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
105	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.864615+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
106	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:24.926916+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
111	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-18 17:11:38.398678+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-18 17:11:38.398678+00
8	t	mixto	24	1	250	0	f	2012	2560	2026-05-27 13:37:12.706797+00	1	albanileria_reforzada	incombustible	f		f	f	25	0.2	0.75	2026-06-08 19:36:01.713236+00
72	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-05 19:50:22.479882+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-08 19:36:01.713236+00
107	t	\N	24	1	\N	\N	t	2009	\N	2026-06-17 19:41:09.907589+00	1	albanileria_reforzada	incombustible	\N	\N	f	f	22	\N	\N	2026-06-17 19:41:09.907589+00
108	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-18 00:00:57.72634+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-18 00:00:57.72634+00
113	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-30 16:18:51.228679+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-30 16:18:51.228679+00
114	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-30 19:37:45.318798+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-06-30 19:37:45.318798+00
116	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-07-01 14:18:26.013561+00	1	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-07-01 14:18:26.013561+00
118	f	habitacional	23	5	715	2	t	2022	62838.8	2026-07-02 19:33:50.869504+00	1	hormigon_armado	incombustible	f	primer_piso	t	t	25	0	0.65	2026-07-02 19:33:50.869504+00
117	f	habitacional	6	2	200	0	f	2007	25000	2026-07-02 19:15:46.214315+00	1	hormigon_armado	incombustible	f	\N	t	t	\N	\N	\N	2026-07-02 19:15:46.214315+00
115	f	habitacional	\N	\N	600	\N	f	2015	57210.62	2026-06-30 20:21:16.683031+00	1	hormigon_armado	incombustible	f		t	t	26	0.1	0.6	2026-06-30 20:21:16.683031+00
\.


--
-- Data for Name: recordatorio; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.recordatorio (id, titulo, detalle, completado, prioridad, tipo_gestion, created_at, fecha_recordatorio) FROM stdin;
13	Iniciar cotización para renovación	El día 20-06-2027 vence la póliza 522222222, por lo que debe comenzar a cotizar para su renovación	f	alta	renovacion_cotizacion	2026-06-30 21:00:38.341692+00	2027-04-20 00:00:00+00
14	Gestionar renovación	El día 20-06-2027 vence la póliza 522222222, por lo que debe gestionar su renovación	f	alta	renovacion	2026-06-30 21:00:38.341692+00	2027-05-31 00:00:00+00
15	Iniciar cotización para renovación	El día 03-07-2027 vence la póliza 51248787, por lo que debe comenzar a cotizar para su renovación	f	alta	renovacion_cotizacion	2026-07-03 19:44:28.663752+00	2027-05-03 00:00:00+00
16	Gestionar renovación	El día 03-07-2027 vence la póliza 51248787, por lo que debe gestionar su renovación	f	alta	renovacion	2026-07-03 19:44:28.663752+00	2027-06-13 00:00:00+00
17	Iniciar cotización para renovación	El día 06-07-2027 vence la póliza 11212121, por lo que debe comenzar a cotizar para su renovación	f	alta	renovacion_cotizacion	2026-07-03 21:40:05.540526+00	2027-05-06 00:00:00+00
18	Gestionar renovación	El día 06-07-2027 vence la póliza 11212121, por lo que debe gestionar su renovación	f	alta	renovacion	2026-07-03 21:40:05.540526+00	2027-06-16 00:00:00+00
19	Iniciar cotización para renovación	El día 01-07-2027 vence la póliza 654654318, por lo que debe comenzar a cotizar para su renovación	f	alta	renovacion_cotizacion	2026-07-03 21:44:19.918165+00	2027-05-01 00:00:00+00
20	Gestionar renovación	El día 01-07-2027 vence la póliza 654654318, por lo que debe gestionar su renovación	f	alta	renovacion	2026-07-03 21:44:19.918165+00	2027-06-11 00:00:00+00
21	Recordatorio de prueba	LLamada de prueba	f	alta	llamada	2026-07-04 20:03:04.458116+00	2026-07-05 09:00:00+00
22	Iniciar cotización para renovación	El día 08-07-2027 vence la póliza 251485124, por lo que debe comenzar a cotizar para su renovación	f	alta	renovacion_cotizacion	2026-07-06 16:21:02.884553+00	2027-05-08 00:00:00+00
23	Gestionar renovación	El día 08-07-2027 vence la póliza 251485124, por lo que debe gestionar su renovación	f	alta	renovacion	2026-07-06 16:21:02.884553+00	2027-06-18 00:00:00+00
24	Contactar con Condominio Parque Mackenna	Preguntar aceptación	f	normal	llamada	2026-07-06 21:15:32.092051+00	2026-07-13 10:00:00+00
9	Iniciar cotización para renovación	El día 01-07-2027 vence la póliza 6549876541, por lo que debe comenzar a cotizar para su renovación	f	alta	renovacion_cotizacion	2026-06-30 14:51:48.101263+00	2027-05-01 00:00:00+00
10	Gestionar renovación	El día 01-07-2027 vence la póliza 6549876541, por lo que debe gestionar su renovación	f	alta	renovacion	2026-06-30 14:51:48.101263+00	2027-05-01 00:00:00+00
2	Condiciones de renovación	Preguntar si acepta las condiciones de renovación	t	normal	llamada	2026-06-25 17:21:19.590091+00	2026-06-23 00:00:00+00
3	Iniciar cotización para renovación	El día 26-06-2027 vence la póliza 65465654, por lo que debe comenzar a cotizar para su renovación	t	alta	renovacion_cotizacion	2026-06-25 17:33:23.98685+00	2027-04-26 00:00:00+00
5	Iniciar cotización para renovación	El día 03-06-2026 vence la póliza 98797987, por lo que debe comenzar a cotizar para su renovación	t	alta	renovacion_cotizacion	2026-06-25 17:36:06.53322+00	2026-04-03 00:00:00+00
7	Iniciar cotización para renovación	El día 03-06-2027 vence la póliza 98754, por lo que debe comenzar a cotizar para su renovación	t	alta	renovacion_cotizacion	2026-06-25 17:37:05.271821+00	2027-04-03 00:00:00+00
4	Gestionar renovación	El día 26-06-2027 vence la póliza 65465654, por lo que debe gestionar su renovación	t	alta	renovacion	2026-06-25 17:33:23.98685+00	2027-04-26 00:00:00+00
6	Gestionar renovación	El día 03-06-2026 vence la póliza 98797987, por lo que debe gestionar su renovación	t	alta	renovacion	2026-06-25 17:36:06.53322+00	2026-04-03 00:00:00+00
8	Gestionar renovación	El día 03-06-2027 vence la póliza 98754, por lo que debe gestionar su renovación	t	alta	renovacion	2026-06-25 17:37:05.271821+00	2027-04-03 00:00:00+00
11	Iniciar cotización para renovación	El día 01-07-2027 vence la póliza 987451254, por lo que debe comenzar a cotizar para su renovación	f	alta	renovacion_cotizacion	2026-06-30 16:33:58.22566+00	2027-05-01 00:00:00+00
12	Gestionar renovación	El día 01-07-2027 vence la póliza 987451254, por lo que debe gestionar su renovación	f	alta	renovacion	2026-06-30 16:33:58.22566+00	2027-06-11 00:00:00+00
\.


--
-- Data for Name: recordatoriocobranzacuotapoliza; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.recordatoriocobranzacuotapoliza (id, id_cuota) FROM stdin;
\.


--
-- Data for Name: recordatoriorenovacionpoliza; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.recordatoriorenovacionpoliza (id, numero_poliza) FROM stdin;
3	65465654
4	65465654
5	98797987
6	98797987
7	98754
8	98754
9	6549876541
10	6549876541
11	987451254
12	987451254
13	522222222
14	522222222
15	51248787
16	51248787
17	11212121
18	11212121
19	654654318
20	654654318
22	251485124
23	251485124
\.


--
-- Data for Name: recordatoriousuario; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.recordatoriousuario (id, rut_usuario, id_prospecto) FROM stdin;
21	20036887-8	\N
2	13358892-2	77
24	19995707-4	118
\.


--
-- Data for Name: rol; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.rol (codigo, nombre) FROM stdin;
GERENTE_OPERACIONES	Gerente de Operaciones
GERENTE_COMERCIAL	Gerente Comercial
GERENTE_GENERAL	Gerente General
ASISTENTE_COMERCIAL	Asistente Comercial
EJECUTIVO_COMERCIAL	Ejecutivo Comercial
EJECUTIVO_SINIESTROS	Ejecutivo de Siniestros
EJECUTIVO_EVALUACION_PROYECTOS	Ejecutivo de Evaluación de Proyectos
ASISTENTE_RENOVACION	Asistente de Renovación
DESARROLLADOR	Desarrollador
EJECUTIVO_RENOVACION_CONDOMINIOS	Ejecutivo de Renovación de Condominios
EJECUTIVO_RENOVACION_LINEAS_PERSONALES	Ejecutivo de Renovación de Líneas Personales
EJECUTIVO_COBRANZA_CONDOMINIOS	Ejecutivo de Cobranza Condominios
EJECUTIVO_COBRANZA_LINEAS_PERSONALES	Ejecutivo de Cobranza Líneas Personales
\.


--
-- Data for Name: rolusuario; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.rolusuario (rut_usuario, codigo_rol) FROM stdin;
21036887-1	EJECUTIVO_COMERCIAL
20036887-8	GERENTE_GENERAL
21036887-3	EJECUTIVO_COMERCIAL
12220101-5	GERENTE_GENERAL
19661132-0	EJECUTIVO_EVALUACION_PROYECTOS
13358892-2	EJECUTIVO_RENOVACION_CONDOMINIOS
11726467-K	EJECUTIVO_RENOVACION_LINEAS_PERSONALES
19041141-9	ASISTENTE_RENOVACION
19995707-4	EJECUTIVO_COMERCIAL
16517406-2	EJECUTIVO_COMERCIAL
19956311-4	EJECUTIVO_COMERCIAL
28372975-3	EJECUTIVO_COMERCIAL
15634751-5	GERENTE_COMERCIAL
\.


--
-- Data for Name: solicitudcotizacion; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.solicitudcotizacion (id, fecha, prioridad, id_proceso_comercial, observaciones, tipo, recotizacion, motivo_recotizacion) FROM stdin;
1	2026-05-13 18:27:51.02949+00	normal	6	\N	espacios_comunes	f	\N
114	2026-06-16 21:53:06.764099+00	normal	293	\N	espacios_comunes	f	\N
116	2026-06-17 13:53:38.55994+00	normal	295	\N	unidades	f	\N
117	2026-06-17 14:20:02.994965+00	alta	293	\N	espacios_comunes	t	Cliente solicita bajar monto asegurado total
118	2026-06-18 23:20:05.954964+00	alta	296	\N	vida_guardia	f	\N
119	2026-06-18 23:29:17.872745+00	normal	297	\N	accidentes_personales	f	\N
120	2026-06-19 16:02:52.393304+00	alta	298	\N	rc_condominio	f	\N
121	2026-06-19 18:02:41.014157+00	alta	299	\N	vida_guardia	f	\N
122	2026-06-21 20:09:49.285648+00	alta	300	\N	accidentes_personales	f	\N
123	2026-06-21 20:23:09.381676+00	alta	300	\N	accidentes_personales	t	Cliente solicita bajar monto asegurado
124	2026-06-21 22:46:49.340845+00	normal	302	\N	accidentes_personales	f	\N
125	2026-06-23 16:45:57.30611+00	normal	303	\N	rc_condominio	f	\N
126	2026-06-30 13:47:43.949936+00	alta	312	\N	unidades	f	\N
127	2026-06-30 16:28:50.400469+00	normal	313	\N	espacios_comunes	f	\N
128	2026-06-30 18:46:18.527198+00	alta	314	\N	unidades	f	\N
129	2026-06-30 20:06:05.616116+00	normal	315	jikjnu	hogar	f	\N
130	2026-06-30 20:24:53.969505+00	normal	319	mmmmmmm	espacios_comunes	f	\N
131	2026-06-30 21:10:12.48974+00	normal	316	\N	rc_condominio	f	\N
132	2026-07-01 14:07:54.089792+00	normal	320	\N	espacios_comunes	f	\N
133	2026-07-02 19:21:12.337708+00	alta	321	Cliente solicita cotización por el monto asegurado actual, separado por torres:\n\n- Torre 1: monto 330000 UF, 315 propietarios.\n- Torre 2: monto 330000 UF, 315 propietarios.\n- Torre 5: monto 60000 UF, 42 propietarios.\n- Torre 6: monto 90000 UF, 43 propietarios.\n- Club House: monto 45000 UF, entre todos los propietarios.	espacios_comunes	f	\N
134	2026-07-02 19:41:21.831638+00	alta	322	\N	espacios_comunes	f	\N
135	2026-07-03 17:58:46.958532+00	normal	322	\N	espacios_comunes	f	\N
136	2026-07-03 21:38:16.559957+00	normal	323	\N	accidentes_personales	f	\N
137	2026-07-04 21:25:05.987412+00	normal	325	\N	unidades	f	\N
138	2026-07-04 21:31:29.368362+00	normal	326	\N	vida_guardia	f	\N
139	2026-07-06 14:42:08.837284+00	alta	328	\N	vehiculos	f	\N
140	2026-07-06 15:08:32.888742+00	normal	332	\N	hogar	f	\N
141	2026-07-06 16:00:49.096324+00	normal	333	\N	unidades	f	\N
142	2026-07-06 16:25:10.857743+00	normal	334	\N	unidades	f	\N
\.


--
-- Data for Name: solicitudcotizacionproductoaccidentespersonales; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.solicitudcotizacionproductoaccidentespersonales (id, actividad, numero_asegurados) FROM stdin;
119	conserjería	3
119	mantención	20
122	Conserjería	10
123	Conserjería	10
124	conserjería	3
124	mantención	10
136	conserjería	2
\.


--
-- Data for Name: solicitudcotizacionproductoresponsabilidadcivil; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.solicitudcotizacionproductoresponsabilidadcivil (id, limite_responsabilidad_civil, actividad_del_condominio) FROM stdin;
120	100	áreas comunes
125	100	administración
131	454	asd
\.


--
-- Data for Name: solicitudcotizacionproductounidades; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.solicitudcotizacionproductounidades (id, monto_asegurado_total, nombre_excel) FROM stdin;
116	319000	excel.xlsx
117	300000	excel.xlsx
126	320000	
128	120000	
137	330000	
141	268000	
142	780000	
\.


--
-- Data for Name: solicitudcotizacionproductovidaguardia; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.solicitudcotizacionproductovidaguardia (id, numero_guardias) FROM stdin;
118	7
121	3
138	3
\.


--
-- Data for Name: sucursal; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.sucursal (id, nombre) FROM stdin;
5	Santiago
6	La Serena
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: crm_admin
--

COPY public.usuario (rut, nombre, correo, telefono, id_sucursal, password_hash, fecha_registro, meta_mensual_uf, habilitado, eliminado, porcentaje_comision, junior) FROM stdin;
20036887-8	Diego Maldonado Zamorano	diego.maldonado@alumnos.ucn.cl	\N	5	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-05-18 14:51:30.706915	\N	t	f	0.3	f
21036887-1	Diego Prieto	prueba_1@jefsei.cl	\N	5	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-05 17:46:03.061811	\N	t	f	0.3	f
19661132-0	Anyel Villalobos	anyel.villalobos@jefsei.cl	\N	6	$2b$12$5ej0FbPfYVlyWvgpAnkpm.BHnepk/6eCMAZZS5S4Q4u4vIjHVg39i	2026-05-18 19:11:24.092712	900	t	f	0.3	f
19995707-4	Antonio Joaquin Maureira Leiva	prueba_0@jefsei.cl	\N	5	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-05 17:44:54.705029	\N	t	f	0.3	f
16517406-2	Denisse Andrea Leyton Retamal	denisse.leyton@jefsei.cl	\N	5	$2b$12$mymr7xZ8VXICV0MvMiDZc.lTc4Gpx.MNrkiodgoXbh7KvTvwtSvPa	2026-05-18 19:12:27.331047	900	t	f	0.3	f
28372975-3	Damián Garcia	prueba_2@jefsei.cl	\N	5	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-05 17:46:03.323643	\N	t	f	0.3	f
13358892-2	María Isabel Gallardo Frede	prueba_7@jefsei.cl	\N	6	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-17 16:58:20.472805	\N	t	f	\N	f
11726467-K	Marisol Olivares	prueba_8@jefsei.cl	\N	6	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-17 16:58:43.081297	\N	t	f	\N	f
19041141-9	Asist renovación	prueba_9@jefsei.cl	\N	6	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-17 16:59:26.159393	\N	t	f	\N	f
19956311-4	Sebastian Cerda Lagos	\N	\N	5	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-05 17:46:03.667693	\N	t	f	0.3	f
15634751-5	Jose Manuel Gaete J.	prueba_6@jefsei.cl	\N	5	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-05 17:46:04.135712	\N	t	f	0.3	f
21036887-3	Sebastian But		\N	6	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-05 17:46:03.41961	\N	f	f	\N	f
12220101-5	Julio Eduardo Flores Veliz	prueba_5@jefsei.cl	\N	5	$2b$12$Pn2uAaFQYLYDUrmUS0Q5iOgrpCLnRQY8mKHk4eC39S07LKRteKj9a	2026-06-05 17:46:03.969417	\N	t	f	0.3	f
\.


--
-- Name: administradorcondominio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.administradorcondominio_id_seq', 2, true);


--
-- Name: cierremensual_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.cierremensual_id_seq', 1, false);


--
-- Name: cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.cliente_id_seq', 98, true);


--
-- Name: coberturariesgo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.coberturariesgo_id_seq', 1, false);


--
-- Name: coberturatiporiesgo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.coberturatiporiesgo_id_seq', 1, false);


--
-- Name: companyseguros_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.companyseguros_id_seq', 15, true);


--
-- Name: comunicadogerencia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.comunicadogerencia_id_seq', 3, true);


--
-- Name: cotizacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.cotizacion_id_seq', 37, true);


--
-- Name: cuota_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.cuota_id_seq', 77, true);


--
-- Name: estudiocomercialcondominio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.estudiocomercialcondominio_id_seq', 5, true);


--
-- Name: etapaprocesocomercialparticular_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.etapaprocesocomercialparticular_id_seq', 1, false);


--
-- Name: gestioncomercial_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.gestioncomercial_id_seq', 1, true);


--
-- Name: historialestadoinformativoprocesocomercial_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.historialestadoinformativoprocesocomercial_id_seq', 391, true);


--
-- Name: lineanegocio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.lineanegocio_id_seq', 1, false);


--
-- Name: planpago_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.planpago_id_seq', 7, true);


--
-- Name: procesocomercial_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.procesocomercial_id_seq', 334, true);


--
-- Name: producto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.producto_id_seq', 26, true);


--
-- Name: prospecto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.prospecto_id_seq', 123, true);


--
-- Name: recordatorio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.recordatorio_id_seq', 24, true);


--
-- Name: solicitudcotizacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.solicitudcotizacion_id_seq', 142, true);


--
-- Name: sucursal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: crm_admin
--

SELECT pg_catalog.setval('public.sucursal_id_seq', 6, true);


--
-- Name: administradorcondominio administradorcondominio_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.administradorcondominio
    ADD CONSTRAINT administradorcondominio_pkey PRIMARY KEY (id);


--
-- Name: cierremensual cierremensual_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cierremensual
    ADD CONSTRAINT cierremensual_pkey PRIMARY KEY (id);


--
-- Name: cierremensual cierremensual_year_mes_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cierremensual
    ADD CONSTRAINT cierremensual_year_mes_key UNIQUE (year, mes);


--
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id);


--
-- Name: coberturariesgo coberturariesgo_id_cobertura_tipo_riesgo_nombre_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.coberturariesgo
    ADD CONSTRAINT coberturariesgo_id_cobertura_tipo_riesgo_nombre_key UNIQUE (id_cobertura_tipo_riesgo, nombre);


--
-- Name: coberturariesgo coberturariesgo_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.coberturariesgo
    ADD CONSTRAINT coberturariesgo_pkey PRIMARY KEY (id);


--
-- Name: coberturatiporiesgo coberturatiporiesgo_nombre_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.coberturatiporiesgo
    ADD CONSTRAINT coberturatiporiesgo_nombre_key UNIQUE (nombre);


--
-- Name: coberturatiporiesgo coberturatiporiesgo_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.coberturatiporiesgo
    ADD CONSTRAINT coberturatiporiesgo_pkey PRIMARY KEY (id);


--
-- Name: companiessugeridas companiessugeridas_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.companiessugeridas
    ADD CONSTRAINT companiessugeridas_pkey PRIMARY KEY (id_company, id_prospecto);


--
-- Name: companycoberturariesgo companycoberturariesgo_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.companycoberturariesgo
    ADD CONSTRAINT companycoberturariesgo_pkey PRIMARY KEY (id_company_seguro, id_cobertura_riesgo);


--
-- Name: companyseguros companyseguros_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.companyseguros
    ADD CONSTRAINT companyseguros_pkey PRIMARY KEY (id);


--
-- Name: comunicadogerencia comunicadogerencia_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.comunicadogerencia
    ADD CONSTRAINT comunicadogerencia_pkey PRIMARY KEY (id);


--
-- Name: cotizacion cotizacion_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cotizacion
    ADD CONSTRAINT cotizacion_pkey PRIMARY KEY (id);


--
-- Name: cuota cuota_id_plan_pago_numero_cuota_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cuota
    ADD CONSTRAINT cuota_id_plan_pago_numero_cuota_key UNIQUE (id_plan_pago, numero_cuota);


--
-- Name: cuota cuota_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cuota
    ADD CONSTRAINT cuota_pkey PRIMARY KEY (id);


--
-- Name: detallecierremensual detallecierremensual_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.detallecierremensual
    ADD CONSTRAINT detallecierremensual_pkey PRIMARY KEY (id_cierre_mensual, numero_poliza);


--
-- Name: estadoinformativoprocesocomercial estadoinformativoprocesocomercial_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.estadoinformativoprocesocomercial
    ADD CONSTRAINT estadoinformativoprocesocomercial_pkey PRIMARY KEY (codigo);


--
-- Name: estudiocomercialcondominio estudiocomercialcondominio_nombre_archivo_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.estudiocomercialcondominio
    ADD CONSTRAINT estudiocomercialcondominio_nombre_archivo_key UNIQUE (nombre_archivo);


--
-- Name: estudiocomercialcondominio estudiocomercialcondominio_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.estudiocomercialcondominio
    ADD CONSTRAINT estudiocomercialcondominio_pkey PRIMARY KEY (id);


--
-- Name: etapaprocesocomercial etapaprocesocomercial_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.etapaprocesocomercial
    ADD CONSTRAINT etapaprocesocomercial_pkey PRIMARY KEY (codigo);


--
-- Name: etapaprocesocomercialparticular etapaprocesocomercialparticul_id_proceso_comercial_codigo_e_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.etapaprocesocomercialparticular
    ADD CONSTRAINT etapaprocesocomercialparticul_id_proceso_comercial_codigo_e_key UNIQUE (id_proceso_comercial, codigo_etapa);


--
-- Name: etapaprocesocomercialparticular etapaprocesocomercialparticular_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.etapaprocesocomercialparticular
    ADD CONSTRAINT etapaprocesocomercialparticular_pkey PRIMARY KEY (id);


--
-- Name: factorcuotascompany factorcuotascompany_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.factorcuotascompany
    ADD CONSTRAINT factorcuotascompany_pkey PRIMARY KEY (id_company, numero_cuotas);


--
-- Name: gestioncomercial gestioncomercial_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.gestioncomercial
    ADD CONSTRAINT gestioncomercial_pkey PRIMARY KEY (id);


--
-- Name: historialestadoinformativoprocesocomercial historialestadoinformativoprocesocomercial_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.historialestadoinformativoprocesocomercial
    ADD CONSTRAINT historialestadoinformativoprocesocomercial_pkey PRIMARY KEY (id);


--
-- Name: lineanegocio linea_negocio_codigo_unique; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.lineanegocio
    ADD CONSTRAINT linea_negocio_codigo_unique UNIQUE (codigo);


--
-- Name: lineanegocio lineanegocio_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.lineanegocio
    ADD CONSTRAINT lineanegocio_pkey PRIMARY KEY (id);


--
-- Name: permiso permiso_descripcion_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.permiso
    ADD CONSTRAINT permiso_descripcion_key UNIQUE (descripcion);


--
-- Name: permiso permiso_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.permiso
    ADD CONSTRAINT permiso_pkey PRIMARY KEY (codigo);


--
-- Name: permisorol permisorol_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.permisorol
    ADD CONSTRAINT permisorol_pkey PRIMARY KEY (codigo_rol, codigo_permiso);


--
-- Name: planificacionprospecto planificacionprospecto_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.planificacionprospecto
    ADD CONSTRAINT planificacionprospecto_pkey PRIMARY KEY (id_prospecto);


--
-- Name: planpago planpago_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.planpago
    ADD CONSTRAINT planpago_pkey PRIMARY KEY (id);


--
-- Name: poliza poliza_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.poliza
    ADD CONSTRAINT poliza_pkey PRIMARY KEY (numero_poliza);


--
-- Name: procesocomercial procesocomercial_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial
    ADD CONSTRAINT procesocomercial_pkey PRIMARY KEY (id);


--
-- Name: producto producto_codigo_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_codigo_key UNIQUE (codigo);


--
-- Name: producto producto_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey PRIMARY KEY (id);


--
-- Name: prospecto prospecto_nombre_riesgo_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospecto
    ADD CONSTRAINT prospecto_nombre_riesgo_key UNIQUE (nombre_riesgo);


--
-- Name: prospecto prospecto_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospecto
    ADD CONSTRAINT prospecto_pkey PRIMARY KEY (id);


--
-- Name: prospecto prospecto_rut_riesgo_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospecto
    ADD CONSTRAINT prospecto_rut_riesgo_key UNIQUE (rut_riesgo);


--
-- Name: prospectocondominio prospectocondominio_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospectocondominio
    ADD CONSTRAINT prospectocondominio_pkey PRIMARY KEY (id);


--
-- Name: recordatorio recordatorio_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatorio
    ADD CONSTRAINT recordatorio_pkey PRIMARY KEY (id);


--
-- Name: recordatoriocobranzacuotapoliza recordatoriocobranzacuotapoliza_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriocobranzacuotapoliza
    ADD CONSTRAINT recordatoriocobranzacuotapoliza_pkey PRIMARY KEY (id);


--
-- Name: recordatoriorenovacionpoliza recordatoriorenovacionpoliza_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriorenovacionpoliza
    ADD CONSTRAINT recordatoriorenovacionpoliza_pkey PRIMARY KEY (id);


--
-- Name: recordatoriousuario recordatoriousuario_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriousuario
    ADD CONSTRAINT recordatoriousuario_pkey PRIMARY KEY (id);


--
-- Name: rol rol_nombre_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_nombre_key UNIQUE (nombre);


--
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (codigo);


--
-- Name: rolusuario rolusuario_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.rolusuario
    ADD CONSTRAINT rolusuario_pkey PRIMARY KEY (rut_usuario, codigo_rol);


--
-- Name: solicitudcotizacion solicitudcotizacion_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacion
    ADD CONSTRAINT solicitudcotizacion_pkey PRIMARY KEY (id);


--
-- Name: solicitudcotizacionproductoaccidentespersonales solicitudcotizacionproductoaccidentespersonales_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacionproductoaccidentespersonales
    ADD CONSTRAINT solicitudcotizacionproductoaccidentespersonales_pkey PRIMARY KEY (id, actividad);


--
-- Name: solicitudcotizacionproductoresponsabilidadcivil solicitudcotizacionproductoresponsabilidadcivil_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacionproductoresponsabilidadcivil
    ADD CONSTRAINT solicitudcotizacionproductoresponsabilidadcivil_pkey PRIMARY KEY (id);


--
-- Name: solicitudcotizacionproductounidades solicitudcotizacionproductounidades_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacionproductounidades
    ADD CONSTRAINT solicitudcotizacionproductounidades_pkey PRIMARY KEY (id);


--
-- Name: solicitudcotizacionproductovidaguardia solicitudcotizacionproductovidaguardia_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacionproductovidaguardia
    ADD CONSTRAINT solicitudcotizacionproductovidaguardia_pkey PRIMARY KEY (id);


--
-- Name: sucursal sucursal_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.sucursal
    ADD CONSTRAINT sucursal_pkey PRIMARY KEY (id);


--
-- Name: usuario usuario_correo_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_correo_key UNIQUE (correo);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (rut);


--
-- Name: usuario usuario_telefono_key; Type: CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_telefono_key UNIQUE (telefono);


--
-- Name: prospecto trigger_usuarios_updated_at; Type: TRIGGER; Schema: public; Owner: crm_admin
--

CREATE TRIGGER trigger_usuarios_updated_at BEFORE UPDATE ON public.prospecto FOR EACH ROW EXECUTE FUNCTION public.actualizar_updated_at();


--
-- Name: cierremensual cierremensual_cerrado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cierremensual
    ADD CONSTRAINT cierremensual_cerrado_por_fkey FOREIGN KEY (cerrado_por) REFERENCES public.usuario(rut);


--
-- Name: cliente cliente_id_prospecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_id_prospecto_fkey FOREIGN KEY (id_prospecto) REFERENCES public.prospecto(id);


--
-- Name: cliente cliente_rut_as_renovacion_asignado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_rut_as_renovacion_asignado_fkey FOREIGN KEY (rut_as_renovacion_asignado) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: cliente cliente_rut_ej_cobranza_asignado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_rut_ej_cobranza_asignado_fkey FOREIGN KEY (rut_ej_cobranza_asignado) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: cliente cliente_rut_ej_renovacion_asignado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_rut_ej_renovacion_asignado_fkey FOREIGN KEY (rut_ej_renovacion_asignado) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: coberturariesgo coberturariesgo_id_cobertura_tipo_riesgo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.coberturariesgo
    ADD CONSTRAINT coberturariesgo_id_cobertura_tipo_riesgo_fkey FOREIGN KEY (id_cobertura_tipo_riesgo) REFERENCES public.coberturatiporiesgo(id) ON DELETE CASCADE;


--
-- Name: companiessugeridas companiessugeridas_id_company_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.companiessugeridas
    ADD CONSTRAINT companiessugeridas_id_company_fkey FOREIGN KEY (id_company) REFERENCES public.companyseguros(id) ON DELETE CASCADE;


--
-- Name: companiessugeridas companiessugeridas_id_prospecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.companiessugeridas
    ADD CONSTRAINT companiessugeridas_id_prospecto_fkey FOREIGN KEY (id_prospecto) REFERENCES public.prospecto(id) ON DELETE CASCADE;


--
-- Name: companycoberturariesgo companycoberturariesgo_id_cobertura_riesgo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.companycoberturariesgo
    ADD CONSTRAINT companycoberturariesgo_id_cobertura_riesgo_fkey FOREIGN KEY (id_cobertura_riesgo) REFERENCES public.coberturariesgo(id) ON DELETE CASCADE;


--
-- Name: companycoberturariesgo companycoberturariesgo_id_company_seguro_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.companycoberturariesgo
    ADD CONSTRAINT companycoberturariesgo_id_company_seguro_fkey FOREIGN KEY (id_company_seguro) REFERENCES public.companyseguros(id) ON DELETE CASCADE;


--
-- Name: comunicadogerencia comunicadogerencia_rut_gerente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.comunicadogerencia
    ADD CONSTRAINT comunicadogerencia_rut_gerente_fkey FOREIGN KEY (rut_gerente) REFERENCES public.usuario(rut);


--
-- Name: cotizacion cotizacion_id_company_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cotizacion
    ADD CONSTRAINT cotizacion_id_company_fkey FOREIGN KEY (id_company) REFERENCES public.companyseguros(id);


--
-- Name: cotizacion cotizacion_id_solicitud_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cotizacion
    ADD CONSTRAINT cotizacion_id_solicitud_fkey FOREIGN KEY (id_solicitud) REFERENCES public.solicitudcotizacion(id);


--
-- Name: cuota cuota_id_plan_pago_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.cuota
    ADD CONSTRAINT cuota_id_plan_pago_fkey FOREIGN KEY (id_plan_pago) REFERENCES public.planpago(id) ON DELETE CASCADE;


--
-- Name: detallecierremensual detallecierremensual_id_cierre_mensual_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.detallecierremensual
    ADD CONSTRAINT detallecierremensual_id_cierre_mensual_fkey FOREIGN KEY (id_cierre_mensual) REFERENCES public.cierremensual(id);


--
-- Name: detallecierremensual detallecierremensual_numero_poliza_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.detallecierremensual
    ADD CONSTRAINT detallecierremensual_numero_poliza_fkey FOREIGN KEY (numero_poliza) REFERENCES public.poliza(numero_poliza);


--
-- Name: detallecierremensual detallecierremensual_rut_ejecutivo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.detallecierremensual
    ADD CONSTRAINT detallecierremensual_rut_ejecutivo_fkey FOREIGN KEY (rut_ejecutivo) REFERENCES public.usuario(rut);


--
-- Name: estadoinformativoprocesocomercial estadoinformativoprocesocomercial_codigo_etapa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.estadoinformativoprocesocomercial
    ADD CONSTRAINT estadoinformativoprocesocomercial_codigo_etapa_fkey FOREIGN KEY (codigo_etapa) REFERENCES public.etapaprocesocomercial(codigo) ON UPDATE CASCADE;


--
-- Name: estudiocomercialcondominio estudiocomercialcondominio_id_solicitud_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.estudiocomercialcondominio
    ADD CONSTRAINT estudiocomercialcondominio_id_solicitud_fkey FOREIGN KEY (id_solicitud) REFERENCES public.solicitudcotizacion(id) ON DELETE CASCADE;


--
-- Name: etapaprocesocomercial etapaprocesocomercial_codigo_siguiente_etapa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.etapaprocesocomercial
    ADD CONSTRAINT etapaprocesocomercial_codigo_siguiente_etapa_fkey FOREIGN KEY (codigo_siguiente_etapa) REFERENCES public.etapaprocesocomercial(codigo) ON UPDATE CASCADE;


--
-- Name: etapaprocesocomercialparticular etapaprocesocomercialparticular_codigo_etapa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.etapaprocesocomercialparticular
    ADD CONSTRAINT etapaprocesocomercialparticular_codigo_etapa_fkey FOREIGN KEY (codigo_etapa) REFERENCES public.etapaprocesocomercial(codigo);


--
-- Name: etapaprocesocomercialparticular etapaprocesocomercialparticular_id_proceso_comercial_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.etapaprocesocomercialparticular
    ADD CONSTRAINT etapaprocesocomercialparticular_id_proceso_comercial_fkey FOREIGN KEY (id_proceso_comercial) REFERENCES public.procesocomercial(id);


--
-- Name: factorcuotascompany factorcuotascompany_id_company_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.factorcuotascompany
    ADD CONSTRAINT factorcuotascompany_id_company_fkey FOREIGN KEY (id_company) REFERENCES public.companyseguros(id) ON DELETE CASCADE;


--
-- Name: gestioncomercial gestioncomercial_id_prospecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.gestioncomercial
    ADD CONSTRAINT gestioncomercial_id_prospecto_fkey FOREIGN KEY (id_prospecto) REFERENCES public.prospecto(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: gestioncomercial gestioncomercial_rut_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.gestioncomercial
    ADD CONSTRAINT gestioncomercial_rut_usuario_fkey FOREIGN KEY (rut_usuario) REFERENCES public.usuario(rut) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: historialestadoinformativoprocesocomercial historialestadoinformativoprocesocome_id_proceso_comercial_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.historialestadoinformativoprocesocomercial
    ADD CONSTRAINT historialestadoinformativoprocesocome_id_proceso_comercial_fkey FOREIGN KEY (id_proceso_comercial) REFERENCES public.procesocomercial(id) ON DELETE CASCADE;


--
-- Name: historialestadoinformativoprocesocomercial historialestadoinformativoprocesocomerc_rut_registrado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.historialestadoinformativoprocesocomercial
    ADD CONSTRAINT historialestadoinformativoprocesocomerc_rut_registrado_por_fkey FOREIGN KEY (rut_registrado_por) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: historialestadoinformativoprocesocomercial historialestadoinformativoprocesocomercial_codigo_estado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.historialestadoinformativoprocesocomercial
    ADD CONSTRAINT historialestadoinformativoprocesocomercial_codigo_estado_fkey FOREIGN KEY (codigo_estado) REFERENCES public.estadoinformativoprocesocomercial(codigo) ON UPDATE CASCADE;


--
-- Name: permisorol permisorol_codigo_permiso_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.permisorol
    ADD CONSTRAINT permisorol_codigo_permiso_fkey FOREIGN KEY (codigo_permiso) REFERENCES public.permiso(codigo) ON UPDATE CASCADE;


--
-- Name: permisorol permisorol_codigo_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.permisorol
    ADD CONSTRAINT permisorol_codigo_rol_fkey FOREIGN KEY (codigo_rol) REFERENCES public.rol(codigo) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: planificacionprospecto planificacionprospecto_id_company_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.planificacionprospecto
    ADD CONSTRAINT planificacionprospecto_id_company_fkey FOREIGN KEY (id_company) REFERENCES public.companyseguros(id) ON DELETE SET NULL;


--
-- Name: planificacionprospecto planificacionprospecto_id_prospecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.planificacionprospecto
    ADD CONSTRAINT planificacionprospecto_id_prospecto_fkey FOREIGN KEY (id_prospecto) REFERENCES public.prospecto(id) ON DELETE CASCADE;


--
-- Name: planpago planpago_numero_poliza_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.planpago
    ADD CONSTRAINT planpago_numero_poliza_fkey FOREIGN KEY (numero_poliza) REFERENCES public.poliza(numero_poliza) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: poliza poliza_id_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.poliza
    ADD CONSTRAINT poliza_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES public.cliente(id);


--
-- Name: poliza poliza_id_company_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.poliza
    ADD CONSTRAINT poliza_id_company_fkey FOREIGN KEY (id_company) REFERENCES public.companyseguros(id);


--
-- Name: poliza poliza_id_proceso_comercial_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.poliza
    ADD CONSTRAINT poliza_id_proceso_comercial_fkey FOREIGN KEY (id_proceso_comercial) REFERENCES public.procesocomercial(id);


--
-- Name: procesocomercial procesocomercial_codigo_estado_actual_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial
    ADD CONSTRAINT procesocomercial_codigo_estado_actual_fkey FOREIGN KEY (codigo_estado_actual) REFERENCES public.estadoinformativoprocesocomercial(codigo) ON UPDATE CASCADE;


--
-- Name: procesocomercial procesocomercial_id_producto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial
    ADD CONSTRAINT procesocomercial_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.producto(id);


--
-- Name: procesocomercial procesocomercial_id_prospecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial
    ADD CONSTRAINT procesocomercial_id_prospecto_fkey FOREIGN KEY (id_prospecto) REFERENCES public.prospecto(id) ON DELETE CASCADE;


--
-- Name: procesocomercial procesocomercial_rut_as_renovacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial
    ADD CONSTRAINT procesocomercial_rut_as_renovacion_fkey FOREIGN KEY (rut_as_renovacion) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: procesocomercial procesocomercial_rut_ej_comercial_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial
    ADD CONSTRAINT procesocomercial_rut_ej_comercial_fkey FOREIGN KEY (rut_ej_comercial) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: procesocomercial procesocomercial_rut_ej_evaluacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial
    ADD CONSTRAINT procesocomercial_rut_ej_evaluacion_fkey FOREIGN KEY (rut_ej_comercial) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: procesocomercial procesocomercial_rut_ej_evaluacion_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial
    ADD CONSTRAINT procesocomercial_rut_ej_evaluacion_fkey1 FOREIGN KEY (rut_ej_evaluacion) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: procesocomercial procesocomercial_rut_ej_renovacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.procesocomercial
    ADD CONSTRAINT procesocomercial_rut_ej_renovacion_fkey FOREIGN KEY (rut_ej_renovacion) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: producto producto_id_linea_negocio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_id_linea_negocio_fkey FOREIGN KEY (id_linea_negocio) REFERENCES public.lineanegocio(id) ON DELETE CASCADE;


--
-- Name: prospecto prospecto_id_linea_negocio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospecto
    ADD CONSTRAINT prospecto_id_linea_negocio_fkey FOREIGN KEY (id_linea_negocio) REFERENCES public.lineanegocio(id);


--
-- Name: prospecto prospecto_rut_ej_comercial_asignado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospecto
    ADD CONSTRAINT prospecto_rut_ej_comercial_asignado_fkey FOREIGN KEY (rut_ej_comercial_asignado) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: prospecto prospecto_rut_ej_evaluacion_asignado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospecto
    ADD CONSTRAINT prospecto_rut_ej_evaluacion_asignado_fkey FOREIGN KEY (rut_ej_evaluacion_asignado) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: prospecto prospecto_rut_registrado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospecto
    ADD CONSTRAINT prospecto_rut_registrado_por_fkey FOREIGN KEY (rut_registrado_por) REFERENCES public.usuario(rut) ON UPDATE CASCADE;


--
-- Name: prospectocondominio prospectocondominio_id_administrador_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospectocondominio
    ADD CONSTRAINT prospectocondominio_id_administrador_fkey FOREIGN KEY (id_administrador) REFERENCES public.administradorcondominio(id) ON DELETE SET NULL;


--
-- Name: prospectocondominio prospectocondominio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.prospectocondominio
    ADD CONSTRAINT prospectocondominio_id_fkey FOREIGN KEY (id) REFERENCES public.prospecto(id) ON DELETE CASCADE;


--
-- Name: recordatoriocobranzacuotapoliza recordatoriocobranzacuotapoliza_id_cuota_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriocobranzacuotapoliza
    ADD CONSTRAINT recordatoriocobranzacuotapoliza_id_cuota_fkey FOREIGN KEY (id_cuota) REFERENCES public.cuota(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: recordatoriocobranzacuotapoliza recordatoriocobranzacuotapoliza_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriocobranzacuotapoliza
    ADD CONSTRAINT recordatoriocobranzacuotapoliza_id_fkey FOREIGN KEY (id) REFERENCES public.recordatorio(id);


--
-- Name: recordatoriorenovacionpoliza recordatoriorenovacionpoliza_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriorenovacionpoliza
    ADD CONSTRAINT recordatoriorenovacionpoliza_id_fkey FOREIGN KEY (id) REFERENCES public.recordatorio(id);


--
-- Name: recordatoriorenovacionpoliza recordatoriorenovacionpoliza_numero_poliza_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriorenovacionpoliza
    ADD CONSTRAINT recordatoriorenovacionpoliza_numero_poliza_fkey FOREIGN KEY (numero_poliza) REFERENCES public.poliza(numero_poliza) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: recordatoriousuario recordatoriousuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriousuario
    ADD CONSTRAINT recordatoriousuario_id_fkey FOREIGN KEY (id) REFERENCES public.recordatorio(id);


--
-- Name: recordatoriousuario recordatoriousuario_id_prospecto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriousuario
    ADD CONSTRAINT recordatoriousuario_id_prospecto_fkey FOREIGN KEY (id_prospecto) REFERENCES public.prospecto(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: recordatoriousuario recordatoriousuario_rut_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.recordatoriousuario
    ADD CONSTRAINT recordatoriousuario_rut_usuario_fkey FOREIGN KEY (rut_usuario) REFERENCES public.usuario(rut) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: rolusuario rolusuario_codigo_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.rolusuario
    ADD CONSTRAINT rolusuario_codigo_rol_fkey FOREIGN KEY (codigo_rol) REFERENCES public.rol(codigo) ON DELETE CASCADE;


--
-- Name: rolusuario rolusuario_rut_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.rolusuario
    ADD CONSTRAINT rolusuario_rut_usuario_fkey FOREIGN KEY (rut_usuario) REFERENCES public.usuario(rut) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: solicitudcotizacion solicitudcotizacion_id_proceso_comercial_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacion
    ADD CONSTRAINT solicitudcotizacion_id_proceso_comercial_fkey FOREIGN KEY (id_proceso_comercial) REFERENCES public.procesocomercial(id);


--
-- Name: solicitudcotizacionproductoaccidentespersonales solicitudcotizacionproductoaccidentespersonales_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacionproductoaccidentespersonales
    ADD CONSTRAINT solicitudcotizacionproductoaccidentespersonales_id_fkey FOREIGN KEY (id) REFERENCES public.solicitudcotizacion(id) ON DELETE CASCADE;


--
-- Name: solicitudcotizacionproductoresponsabilidadcivil solicitudcotizacionproductoresponsabilidadcivil_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacionproductoresponsabilidadcivil
    ADD CONSTRAINT solicitudcotizacionproductoresponsabilidadcivil_id_fkey FOREIGN KEY (id) REFERENCES public.solicitudcotizacion(id) ON DELETE CASCADE;


--
-- Name: solicitudcotizacionproductounidades solicitudcotizacionproductounidades_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacionproductounidades
    ADD CONSTRAINT solicitudcotizacionproductounidades_id_fkey FOREIGN KEY (id) REFERENCES public.solicitudcotizacion(id) ON DELETE CASCADE;


--
-- Name: solicitudcotizacionproductovidaguardia solicitudcotizacionproductovidaguardia_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.solicitudcotizacionproductovidaguardia
    ADD CONSTRAINT solicitudcotizacionproductovidaguardia_id_fkey FOREIGN KEY (id) REFERENCES public.solicitudcotizacion(id) ON DELETE CASCADE;


--
-- Name: usuario usuario_id_sucursal_fkey; Type: FK CONSTRAINT; Schema: public; Owner: crm_admin
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_id_sucursal_fkey FOREIGN KEY (id_sucursal) REFERENCES public.sucursal(id);


--
-- PostgreSQL database dump complete
--

\unrestrict hfflf29O8KgnDhUR0vxF3igMXRWNyBuQ81E6hDcqnJ7cALRDfKPwZYmd44fc5Bt

