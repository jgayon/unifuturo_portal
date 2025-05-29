// import React from 'react';
// import { useNavigate } from 'react-router-dom';
// import './ProgramSelection.css';

// const ProgramSelection = () => {
//   const navigate = useNavigate();

//   const handleClick = (program) => {
//     navigate(`/subjects/${program}`);
//   };

//   return (
//     <div className="program-selection">
//       <h2>Select a Program</h2>
//       <div className="program-grid">
//         <div onClick={() => handleClick('engineering')} className="program-card">Engineering</div>
//         <div onClick={() => handleClick('medicine')} className="program-card">Medicine</div>
//         <div onClick={() => handleClick('law')} className="program-card">Law</div>
//       </div>
//     </div>
//   );
// };

// export default ProgramSelection

// si
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ProgramSelection.css';

const ProgramSelection = () => {
  const navigate = useNavigate();

  const handleClick = (program) => {
    navigate(`/subjects/${program}`);
  };

  const programs = [
    { name: 'Ingeniería', id: 'engineering' },
    { name: 'Medicina', id: 'medicine' },
    { name: 'Derecho', id: 'law' },
    { name: 'Administracion de Empresas', id: 'business' },
    { name: 'Arquitectura', id: 'architecture' },
    { name: 'Ciencia de Datos', id: 'datascience' }
  ];

  return (
    <div className="program-selection">
      <h2>Seleccione un Programa</h2>
      <div className="program-grid">
        {programs.map((p) => (
          <div key={p.id} onClick={() => handleClick(p.id)} className="program-card">
            {p.name}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgramSelection;