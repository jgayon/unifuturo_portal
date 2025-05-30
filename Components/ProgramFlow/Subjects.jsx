import React from 'react';
import { useParams } from 'react-router-dom';
import './Subjects.css';

const programs = {
  engineering: {
    name: 'Ingeniería',
    semesters: [
      ['Matemáticas I', 'Física I', 'Programación I'],
      ['Matemáticas II', 'Física II', 'Estructuras de Datos'],
      ['Álgebra Lineal', 'Electrónica', 'Bases de Datos'],
      ['Sistemas Operativos', 'Redes de Computadoras', 'Ingeniería de Software']
    ]
  },
  medicine: {
    name: 'Medicina',
    semesters: [
      ['Biología Celular', 'Anatomía I', 'Bioquímica'],
      ['Anatomía II', 'Fisiología', 'Genética'],
      ['Microbiología', 'Farmacología', 'Patología General'],
      ['Salud Pública', 'Psicología Médica', 'Semiología']
    ]
  },
  law: {
    name: 'Derecho',
    semesters: [
      ['Introducción al Derecho', 'Derecho Romano', 'Historia del Derecho'],
      ['Derecho Constitucional', 'Derecho Civil I', 'Teoría del Estado'],
      ['Derecho Penal I', 'Derecho Procesal', 'Derecho Laboral'],
      ['Filosofía del Derecho', 'Derecho Administrativo', 'Derechos Humanos']
    ]
  },
  business: {
    name: 'Administración de Empresas',
    semesters: [
      ['Calculo 1 (ANEC)', 'Contabilidad', 'Calculo 2 (ANEC)', 'Calculo 3 (ANEC)', 'Economia'],
      ['Introducción a la Administración', 'Contabilidad General', 'Matemáticas Financieras'],
      ['Microeconomía', 'Gestión del Talento Humano', 'Estadística', 'Costos y Presupuestos'],
      ['Planeacion Financiera', 'Macroeconomia', 'Mercadeo', 'Gestión Financiera', 'Marketing'],
    ]
  },
  architecture: {
    name: 'Arquitectura',
    semesters: [
      ['Fundamentos de Diseño', 'Geometría Descriptiva', 'Historia de la Arquitectura I'],
      ['Diseño Arquitectónico I', 'Construcción I', 'Materiales de Construcción'],
      ['Diseño Arquitectónico II', 'Teoría de la Arquitectura', 'Instalaciones Sanitarias'],
      ['Historia de la Arquitectura II', 'Construcción II', 'Representación Digital']
    ]
  },
  datascience: {
    name: 'Ciencia de Datos',
    semesters: [
      ['Matemáticas Discretas', 'Fundamentos de Programación', 'Estadística I'],
      ['Programación en Python', 'Probabilidades y Estadística II', 'Bases de Datos'],
      ['Minería de Datos', 'Machine Learning', 'Visualización de Datos'],
      ['Big Data', 'Procesamiento de Lenguaje Natural', 'Deep Learning']
    ]
  }
};

const Subjects = () => {
  const { program } = useParams();
  const selected = programs[program];

  if (!selected) return <h2>Programa no encontrado</h2>;

  return (
    <div className="subjects-page">
      <h2>{selected.name} - Plan de Estudios</h2>
      <div className="semesters">
        {selected.semesters.map((courses, index) => (
          <div className="semester" key={index}>
            <h3>Semestre {index + 1}</h3>
            <ul>
              {courses.map((course, i) => <li key={i}>{course}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Subjects;